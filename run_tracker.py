import csv
import os
from datetime import datetime
import uuid
import pandas as pd

class BrassTracker:
    def __init__(self):
        # 🎲 基础对局控制状态
        self.match_id = ""
        self.players = []             # 动态行动顺位列表，存放纯名字: ["alex", "sam", ...]
        self.era = "Canal Era"
        self.round_id = 1
        self.current_player_idx = 0   # 当前行动玩家的索引指针
        self.action_num = 1           # 当前是该玩家的第 1 还是第 2 个行动
        self.game_over = False
        self.player_states = {}       # 玩家实时的手牌、金钱、消费状态池
        
        # 📂 1. 绝对路径绑定（规范的 prod 与 config 隔离架构）
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        # 📊 事实表路径（本地动态业务数据 - 用于后续追加写入）
        self.file_match = os.path.join(BASE_DIR, "data", "prod", "fact_match_players.csv")
        self.file_actions = os.path.join(BASE_DIR, "data", "prod", "fact_action_events.csv")
        self.file_card_flows = os.path.join(BASE_DIR, "data", "prod", "fact_card_flows.csv")     
        self.file_economy = os.path.join(BASE_DIR, "data", "prod", "fact_player_economy.csv")
        self.file_turn_order = os.path.join(BASE_DIR, "data", "prod", "fact_turn_order.csv")

        # ⚙️ 维度表路径（只读配置规则）
        self.file_dim_locations = os.path.join(BASE_DIR, "data", "config", "dim_locations.csv")
        self.file_dim_links = os.path.join(BASE_DIR, "data", "config", "dim_board_links.csv")
        self.file_dim_cards = os.path.join(BASE_DIR, "data", "config", "dim_cards.csv")         
        
        # 🚀 2. 使用 Pandas 从只读配置中提取初始常量（有容错）
        try:
            self.LOCATIONS = pd.read_csv(self.file_dim_locations)["location_name"].dropna().unique().tolist()
        except Exception as e:
            print(f"⚠️ 无法读取 {self.file_dim_locations}: {e}; 将使用空地点列表。")
            self.LOCATIONS = []
        try:
            self.INDUSTRIES = pd.read_csv(self.file_dim_locations)["slot_industry"].dropna().unique().tolist()
        except Exception as e:
            print(f"⚠️ 无法读取产业维度: {e}; 将使用空产业列表。")
            self.INDUSTRIES = []
        try:
            self.LINKS_CANAL = pd.read_csv(self.file_dim_links).query("link_type in ['Both', 'Canal']")["link"].dropna().unique().tolist()
        except Exception as e:
            print(f"⚠️ 无法读取 {self.file_dim_links}: {e}; Canal 链接列表将为空。")
            self.LINKS_CANAL = []
        try:
            self.LINKS_RAIL = pd.read_csv(self.file_dim_links).query("link_type in ['Both', 'Rail']")["link"].dropna().unique().tolist()
        except Exception as e:
            print(f"⚠️ 无法读取 {self.file_dim_links}: {e}; Rail 链接列表将为空。")
            self.LINKS_RAIL = []
        try:
            self.CARDS = pd.read_csv(self.file_dim_cards)["card_contents"].dropna().tolist()
        except Exception as e:
            print(f"⚠️ 无法读取 {self.file_dim_cards}: {e}; 使用简单后备卡池。")
            # 轻量后备卡池，保证交互能继续
            self.CARDS = ["Coal", "Iron", "Pottery", "Beer", "Textiles", "Glass"]

        # 流程控制配置
        self.ACTION_TYPES = ["Loan", "Link", "Develop", "Build", "Scout", "Sell", "Skip"]
        self.AVAILABLE_COLORS = ["White", "Purple", "Red", "Yellow"]

        # 初始化 max_actions 为当前时代/回合的规则
        self.max_actions = 1 if (self.era == "Canal Era" and self.round_id == 1) else 2
        # max_rounds 会在 advance_state 中根据玩家数设定

    def init_match(self):
        print("=========================================")
        print("   《工业革命：伯明翰》硬核动作录入系统 v1.5   ")
        print("=========================================")
        
        # 1. 使用 Pandas 提取最大对局 ID 
        max_id_num = 0
        if os.path.isfile(self.file_match):
            try:
                df_match = pd.read_csv(self.file_match, usecols=["match_id"], dtype={"match_id": str})
                valid_ids = pd.to_numeric(df_match["match_id"], errors='coerce')
                if not valid_ids.isna().all():
                    max_id_num = int(valid_ids.max())
            except Exception as e:
                print(f"ℹ️ 提示: 读取历史对局表时未找到有效 ID (将从 0001 开始): {e}")

        self.match_id = f"{(max_id_num + 1):04d}"
        print(f"🤖 系统已自动为您创建全新对局，ID 分配为: 【{self.match_id}】")

        # 2. 校验玩家人数
        while True:
            try:
                num_players = int(input("请输入玩家人数 (2-4): ").strip())
                if 2 <= num_players <= 4:
                    break
                print("❌ 人数限制！《黄铜：伯明翰》只支持 2 到 4 人游戏。")
            except ValueError:
                print("❌ 输入无效！请输入数字 2、3 或 4。")

        # 3. 输入昵称并选择颜色
        temp_players = []  
        for i in range(num_players):
            name = input(f"\n[顺位 {i+1}] 请输入玩家昵称: ").strip()
            chosen_color = self.get_choice(self.AVAILABLE_COLORS, f"请选择 【{name}】 的玩家颜色")
            if chosen_color is None:
                # fallback: pick first available
                chosen_color = self.AVAILABLE_COLORS[0] if self.AVAILABLE_COLORS else "None"
            if chosen_color in self.AVAILABLE_COLORS:
                self.AVAILABLE_COLORS.remove(chosen_color)
            temp_players.append({"name": name, "color": chosen_color})
            
        # 4. ⚙️ 核心前置：从维度配置中提取初始卡牌总池，并让玩家选好 8 张牌
        # self.CARDS already loaded with fallback in __init__

        print("\n--- 🃏 开始录入每位玩家的 8 张开局初始手牌 ---")
        for p in temp_players:
            print(f"\n👉 请为玩家 【{p['name']}】 依次选择 8 张手牌（当前牌堆剩余: {len(self.CARDS)} 张）：")
            initial_hand = []
            for i in range(8):
                if not self.CARDS:
                    print("⚠️ 公共卡池为空，停止补牌。")
                    break
                prompt_msg = f"请选择【{p['name']}】的第 {i+1}/8 张卡牌"
                chosen_card = self.get_choice(self.CARDS, prompt_msg)
                if chosen_card is None:
                    # user cancelled selection loop - break out
                    break
                initial_hand.append(chosen_card)
                # 从公共池销账（如果存在）
                try:
                    self.CARDS.remove(chosen_card)
                except ValueError:
                    pass
            
            # 🌟 把选好的手牌列表直接挂在当前玩家的临时字典里
            p["initial_hand"] = initial_hand

        # 5. 🛠️ 整理并追加写入对局玩家事实表（增加手牌列字段）
        file_exists = os.path.isfile(self.file_match)
        headers = [
            "match_id", "date", 
            "player_1_name", "player_1_color", "player_1_hand",
            "player_2_name", "player_2_color", "player_2_hand",
            "player_3_name", "player_3_color", "player_3_hand",
            "player_4_name", "player_4_color", "player_4_hand"
        ]
        
        # 组装行数据
        row_data = [self.match_id, datetime.now().strftime("%Y-%m-%d")]
        for p in temp_players:
            # 💡 这里使用 str(p["initial_hand"])，把 Python 列表完美转型为文本字符串存入单个单元格
            row_data.extend([p["name"], p["color"], str(p["initial_hand"])])
            
        # 自动补齐 4 人局多余的空格（如 3 人局时，自动补足 player_4 的 name, color, hand 空白）
        slot_needed = len(headers) - len(row_data)
        if slot_needed > 0:
            row_data.extend([""] * slot_needed)
            
        os.makedirs(os.path.dirname(self.file_match), exist_ok=True)
        with open(self.file_match, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(headers)
            writer.writerow(row_data)
            
        # 6. 🧠 无缝刷新到内存状态池中
        self.players = [p["name"] for p in temp_players]  
        self.player_states = {}                           
        
        for p in temp_players:
            self.player_states[p["name"]] = {
                "money": 30,              
                "income_level": 0,    
                "hand": p["initial_hand"], # 保持为干净的真正的 List 供内存追踪  
                "round_spent": 0          
            }
            
        print(f"\n🎉 对局 {self.match_id} 初始化成功！所有玩家状态、初始手牌已绑定并成功落盘。")

    def _action_loan(self, player):
        print(f"💰 【{player}】 正在执行贷款行动...")
        # 核心逻辑：贷款为 +30 现金（通过 cost=-30 传入），并调低收入
        self._track_economy(player, cost=-30, income_delta=-3)

    def _action_skip(self, player):
        print(f"💤 【{player}】 弃牌跳过行动。")
        self._track_economy(player, cost=0)

    # ==========================================
    # 🌟 核心分发器：用 record_action 去 call 那些 def
    # ==========================================
    def record_action(self):
        current_player = self.players[self.current_player_idx]
        state = self.player_states[current_player]
        print(f"\n📢 轮到玩家 【{current_player}】 执行第 {self.action_num} 次行动")
        
        # 1. 追踪手牌流向 (需求 2)
        action_card = self._track_card_flow(current_player)

        # capture pre-action economy state
        pre_cash = state.get("money", 0)
        pre_income = state.get("income_level", 0)

        # 2. 选择行动类型并动态分发
        action_type = self.get_choice(self.ACTION_TYPES, "请选择行动内容")
        if action_type is None:
            print("⚠️ 未选择行动类型，跳过本次行动。")
            return
        
        # 映射字典：动态调用实例方法
        action_mapping = {
            "Loan": self._action_loan,
            # other handlers to be implemented
            "Skip": self._action_skip
        }

        action_fn = action_mapping.get(action_type)
        if action_fn:
            action_fn(current_player)
        else:
            print(f"ℹ️ 动作 {action_type} 尚未实现，已跳过执行步骤。")

        # capture post-action economy state
        post_cash = state.get("money", 0)
        post_income = state.get("income_level", 0)
        cash_delta = post_cash - pre_cash

        # persist action-level fact row to file_actions
        os.makedirs(os.path.dirname(self.file_actions), exist_ok=True)
        file_exists = os.path.isfile(self.file_actions)
        headers = [
            "action_uuid", "match_id", "player_id", "era", "round_id", "action_num",
            "pre_cash", "pre_income", "action_type", "card_played", "cash_delta", "post_cash", "post_income", "timestamp"
        ]
        row = [
            uuid.uuid4().hex[:8], self.match_id, current_player, self.era, self.round_id, self.action_num,
            pre_cash, pre_income, action_type, action_card or "", cash_delta, post_cash, post_income, datetime.now().isoformat()
        ]
        with open(self.file_actions, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(headers)
            writer.writerow(row)

        print("\n=== 行动已记录 (action fact + card flow + economy fact) ===")

    # ==========================================
    # 🌟 重构核心 2：手牌流动追踪事实表流
    # ==========================================
    def _track_card_flow(self, player):
        state = self.player_states[player]
        start_hand = list(state.get("hand", [])) # 深度复制初始手牌状态
        
        if not start_hand:
            print(f"⚠️ 玩家 {player} 当前手牌为空，跳过出牌阶段。")
            return ""

        print(f"🃏 [手牌流管理] 玩家当前手牌为: {start_hand}")
        
        # 输入打出的牌（带维度的可选校验更好，这里支持手动输入）
        action_card = self.get_choice(state["hand"], f"请选择【{player}】本次行动【打出】的卡牌")
        if action_card is None:
            print("⚠️ 未选择卡牌，跳过出牌。")
            return ""
        try:
            state["hand"].remove(action_card)
        except ValueError:
            # card may have been already removed due to race or input, ignore
            pass
            
        refilled_cards = []
        if self.action_num == self.max_actions:
            for idx in range(self.max_actions):
                if len(self.CARDS) > 0:
                    refill = self.get_choice(self.CARDS, f"请选择补充的第 {idx+1}/{self.max_actions} 张卡牌")
                    if refill is None:
                        break
                    state["hand"].append(refill)
                    refilled_cards.append(refill)
                    try:
                        self.CARDS.remove(refill)
                    except ValueError:
                        pass
                else:
                    print("⚠️ 提示: 公共牌库已空，无法继续补牌！")
                    break
                
        end_hand = list(state.get("hand", []))
        
        # 写入事实表 fact_card_flows.csv
        os.makedirs(os.path.dirname(self.file_card_flows), exist_ok=True)
        file_exists = os.path.isfile(self.file_card_flows)
        headers = ["match_id", "era", "round_id", "player_name", "action_num", "start_hand", "action_card", "end_hand"]
        row_data = [self.match_id, self.era, self.round_id, player, self.action_num, str(start_hand), action_card or "", str(end_hand)]
        with open(self.file_card_flows, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(headers)
            writer.writerow(row_data)
            
        return action_card

    # ==========================================
    # 🌟 重构核心 3：自动计算经济变动并记账
    # ==========================================
    def _track_economy(self, player, cost, income_delta=0):
        state = self.player_states[player]
        money_before = state.get("money", 0)
        income_before = state.get("income_level", 0)
        
        # 内存更新: convention in this code: cost > 0 means expense, cost < 0 means cash gain
        state["money"] -= cost
        state["income_level"] += income_delta
        
        # 只有正数开销才算进重排顺位的累计消费池中（贷款带来的负花费不进入统计）
        if cost > 0:
            state["round_spent"] = state.get("round_spent", 0) + cost
            
        money_after = state.get("money", 0)
        income_after = state.get("income_level", 0)
        
        print(f"📊 经济同步成功 -> 现金: £{money_before} -> £{money_after} | 收入等级: {income_before} -> {income_after}")
        
        # 写入事实表 fact_player_economy.csv
        os.makedirs(os.path.dirname(self.file_economy), exist_ok=True)
        file_exists = os.path.isfile(self.file_economy)
        headers = ["match_id", "era", "round_id", "player_name", "action_num", "income_level", "money_before", "cost", "money_after"]
        row_data = [self.match_id, self.era, self.round_id, player, self.action_num, income_after, money_before, cost, money_after]
        with open(self.file_economy, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(headers)
            writer.writerow(row_data)

    # ==========================================
    # 🌟 重构核心 4：状态步进与基于轮消费重排顺位
    # ==========================================
    def advance_state(self):
        """
        负责推进游戏状态：切换玩家 -> 递增行动数 -> 递增回合 -> 切换时代
        """
        # 1. 动态判断当前时代第一轮是否只有 1 次行动（运河时代第一轮每人只有1动）
        is_canal_first_round = (self.era == "Canal Era" and self.round_id == 1)
        self.max_actions = 1 if is_canal_first_round else 2
        
        # 2. 🎮 对应人数的最大回合数（2人10回合，3人9回合，4人8回合）
        player_count = len(self.players)
        self.max_rounds = {2: 10, 3: 9, 4: 8}.get(player_count, 8)
            
        # 3. 推进当前玩家的行动计数
        if self.action_num < self.max_actions:
            self.action_num += 1
            return  # 还在当前玩家的回合内，继续下一次行动
            
        # 4. 如果当前玩家的行动轮完了，重置行动数，切换到下一个玩家
        self.action_num = 1
        self.current_player_idx += 1
        
        # 5. 🌟 核心控制点：如果所有玩家都轮过了一遍，说明当前【大轮/Round】结束
        if self.current_player_idx >= player_count:
            print(f"\n🔄 【第 {self.round_id} 轮结束】所有玩家行动完毕，开始结算本轮...")
            
            # 🔴 核心重构 4 落地：根据本轮消费重排下一轮顺位，并追加写入事实表
            self._reorder_turn_order()
            
            # 💡 提示：可以在这里顺便执行每轮结束的发收入/扣贷款利息逻辑（发放 self.player_states[p]["income_level"] 对应的钱）
            # self._collect_income() 
            
            # 每一个大轮结束，重置所有玩家在这一大轮里的消费计数器
            for p in self.players:
                self.player_states[p]["round_spent"] = 0
                
            # 指针归零，回到新顺位的第一位玩家
            self.current_player_idx = 0  
            
            # 🔢 检测时代更替还是递增回合
            # Compare round number to max_rounds (not max_actions)
            if self.round_id >= self.max_rounds:
                # 如果当前已经是该时代的最后一轮了
                if self.era == "Canal Era":
                    print(f"\n🌅 【Canal Era】已完成最大回合数 {self.max_rounds}！")
                    print("👉 请进行【运河时代算分】。准备切入铁路时代...")
                    self.era = "Rail Era"
                    self.round_id = 1    # 重置回合数，从铁路时代第 1 轮重新开始
                else:
                    print(f"\n🏁 【Rail Era】已完成最大回合数 {self.max_rounds}！")
                    print("🏆 全场游戏录入结束！请在事实表中查看最终对局流水。")
                    self.game_over = True # 标记整个游戏结束
            else:
                # 没到时代终点，正常进入下一大轮
                self.round_id += 1

    def _reorder_turn_order(self):
        """
        根据本轮总消费重排顺位（升序：花钱越少越靠前）。
        Python 的 sorted() 方法具备稳定性（Stable Sort），当消费完全一致时，会自动保留上一轮原有的相对次序，完全契合黄铜官方规则！
        """
        # 使用 lambda 按内存里的 round_spent 升序排列
        sorted_players = sorted(self.players, key=lambda p: self.player_states[p].get("round_spent", 0))
        
        print("\n🏆 === 下一轮新行动顺位已生成 ===")
        os.makedirs(os.path.dirname(self.file_turn_order), exist_ok=True)
        file_exists = os.path.isfile(self.file_turn_order)
        headers = ["match_id", "era", "round_id", "player_name", "total_spent_this_round", "next_round_order"]
        
        for idx, p_name in enumerate(sorted_players):
            spent = self.player_states[p_name].get("round_spent", 0)
            new_order = idx + 1
            print(f" 🔹 顺位 [{new_order}]: {p_name} (本轮消费: £{spent})")
            
            # 记录数据进事实表 fact_turn_order.csv
            row_data = [self.match_id, self.era, self.round_id, p_name, spent, new_order]
            with open(self.file_turn_order, mode="a", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(headers)
                    file_exists = True  # 保证多条循环时表头只写一次
                writer.writerow(row_data)
        
        # 🔴 核心覆盖：将排好序的新顺位刷新到状态机
        self.players = sorted_players

    def get_choice(self, options, prompt):
        # guard empty options
        if not options:
            print(f"⚠️ 可选项为空 ({prompt})。")
            return None
        print(f"\n--- {prompt} ---")
        for i, opt in enumerate(options):
            print(f"[{i+1}] {opt}")
        while True:
            user_input = input("选择对应数字: ").strip()
            try:
                idx = int(user_input) - 1
                if 0 <= idx < len(options):
                    chosen_opt = options[idx]
                    confirm = input(f" 👉 确认选择 【{chosen_opt}】 吗？[Y/N] (默认 Y): ").strip().upper()
                    if confirm == 'N':
                        print("↩️ 已取消选择，请重新输入数字。")
                        continue  
                    return chosen_opt
            except ValueError:
                pass
            print("❌ 输入无效，请重新选择。")

    def run(self):
        try:
            self.init_match()
            # 循环录入控制
            while not self.game_over:
                self.record_action()
                self.advance_state()

                # normal termination is based on game_over or era/round logic
            print("\n🏁 对局录入完毕，所有数据已落盘至 data/prod/ 目录。")
        except KeyboardInterrupt:
            print("\n🛑 已收到中断 (Ctrl+C)，程序退出。")

if __name__ == "__main__":
    tracker = BrassTracker()
    tracker.run()
