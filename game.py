"""控制台扫雷游戏 (Console Minesweeper)

操作说明：
    - 输入坐标揭开格子，例如:  a5  或  A5
    - 在坐标前加 f 标记/取消标记地雷，例如:  f a5
    - 输入 r 重新开始
    - 输入 q 退出游戏
"""

import random
import sys

# ====== 游戏常量 ======
ROWS = 10
COLS = 10
MINES = 10

# 单元格显示符号
HIDDEN = "■"      # 未揭开
FLAG = "⚑"        # 已标记
MINE = "✱"        # 地雷
EMPTY = "·"       # 已揭开且周围无雷

# 列标签 A..J
COL_LABELS = [chr(ord("A") + i) for i in range(COLS)]


class Minesweeper:
    def __init__(self):
        self.reset()

    # ---------- 初始化 ----------
    def reset(self):
        """重置棋盘到初始状态。地雷在首次揭开时再放置，避免第一步就踩雷。"""
        self.mines = [[False] * COLS for _ in range(ROWS)]
        self.revealed = [[False] * COLS for _ in range(ROWS)]
        self.flagged = [[False] * COLS for _ in range(ROWS)]
        self.adjacent = [[0] * COLS for _ in range(ROWS)]
        self.mines_placed = False
        self.game_over = False
        self.won = False

    def place_mines(self, safe_r, safe_c):
        """在棋盘上随机放置地雷，确保 (safe_r, safe_c) 及其相邻格不是地雷。"""
        forbidden = set()
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                rr, cc = safe_r + dr, safe_c + dc
                if 0 <= rr < ROWS and 0 <= cc < COLS:
                    forbidden.add((rr, cc))

        candidates = [
            (r, c)
            for r in range(ROWS)
            for c in range(COLS)
            if (r, c) not in forbidden
        ]
        for (r, c) in random.sample(candidates, MINES):
            self.mines[r][c] = True

        # 计算每个格子相邻的地雷数
        for r in range(ROWS):
            for c in range(COLS):
                if self.mines[r][c]:
                    continue
                count = 0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < ROWS and 0 <= cc < COLS and self.mines[rr][cc]:
                            count += 1
                self.adjacent[r][c] = count

        self.mines_placed = True

    # ---------- 操作 ----------
    def reveal(self, r, c):
        """揭开格子，自动扩展空白区域。返回 True 表示踩雷。"""
        if not self.mines_placed:
            self.place_mines(r, c)

        if self.flagged[r][c] or self.revealed[r][c]:
            return False

        if self.mines[r][c]:
            self.revealed[r][c] = True
            self.game_over = True
            return True

        # BFS 自动展开
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if self.revealed[cr][cc] or self.flagged[cr][cc]:
                continue
            self.revealed[cr][cc] = True
            if self.adjacent[cr][cc] == 0:
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = cr + dr, cc + dc
                        if (
                            0 <= nr < ROWS
                            and 0 <= nc < COLS
                            and not self.revealed[nr][nc]
                            and not self.mines[nr][nc]
                        ):
                            stack.append((nr, nc))

        self._check_win()
        return False

    def toggle_flag(self, r, c):
        """切换格子的旗帜状态。"""
        if self.revealed[r][c]:
            return False
        self.flagged[r][c] = not self.flagged[r][c]
        return True

    def _check_win(self):
        """所有非雷格子都已揭开则胜利。"""
        for r in range(ROWS):
            for c in range(COLS):
                if not self.mines[r][c] and not self.revealed[r][c]:
                    return
        self.won = True
        self.game_over = True

    # ---------- 渲染 ----------
    def render(self):
        flags_used = sum(1 for r in range(ROWS) for c in range(COLS) if self.flagged[r][c])
        print()
        print(f"  剩余地雷数: {MINES - flags_used}    旗帜数: {flags_used}")
        # 列标题
        header = "    " + "  ".join(COL_LABELS)
        print(header)
        print("   " + "-" * (COLS * 3 + 1))
        for r in range(ROWS):
            row_label = f"{r + 1:>2}"
            cells = []
            for c in range(COLS):
                cells.append(self._cell_str(r, c))
            print(f"{row_label} | " + "  ".join(cells))
        print()

    def _cell_str(self, r, c):
        # 游戏结束时显示所有地雷
        if self.game_over and self.mines[r][c]:
            # 如果玩家正确标记了地雷，依然显示旗帜
            if self.flagged[r][c]:
                return FLAG
            return MINE
        # 游戏结束时显示错误标记的旗帜
        if self.game_over and self.flagged[r][c] and not self.mines[r][c]:
            return "✗"
        if self.flagged[r][c]:
            return FLAG
        if not self.revealed[r][c]:
            return HIDDEN
        n = self.adjacent[r][c]
        if n == 0:
            return EMPTY
        return str(n)


# ====== 输入解析 ======
def parse_coord(token):
    """解析 'a5' / 'A5' / '5a' 等坐标字符串，返回 (row, col) 或 None。"""
    token = token.strip().lower()
    if not token:
        return None
    letters = "".join(ch for ch in token if ch.isalpha())
    digits = "".join(ch for ch in token if ch.isdigit())
    # Reject: no letter, no digit, multi-letter, or extra characters
    if len(letters) != 1 or not digits:
        return None
    # Ensure no trailing garbage: token must be exactly letters+digits in either order
    if letters + digits != token and digits + letters != token:
        return None
    col = ord(letters) - ord("a")
    try:
        row = int(digits) - 1
    except ValueError:
        return None
    if not (0 <= row < ROWS and 0 <= col < COLS):
        return None
    return row, col


def parse_command(line):
    """解析整行命令。返回元组：
        ('reveal', r, c)
        ('flag', r, c)
        ('restart',)
        ('quit',)
        ('help',)
        ('invalid', reason)
    """
    s = line.strip().lower()
    if not s:
        return ("invalid", "请输入命令。")
    if s in ("r", "restart", "重置", "重开"):
        return ("restart",)
    if s in ("q", "quit", "exit", "退出"):
        return ("quit",)
    if s in ("h", "help", "帮助", "?"):
        return ("help",)

    parts = s.split()
    if parts[0] in ("f", "flag", "标记"):
        if len(parts) < 2:
            return ("invalid", "请提供要标记的坐标，例如:  f a5")
        coord = parse_coord(parts[1])
        if coord is None:
            return ("invalid", "坐标无效，请使用如  a5  这样的格式。")
        return ("flag", coord[0], coord[1])

    # 否则视为揭开坐标
    coord = parse_coord(parts[0])
    if coord is None:
        return ("invalid", "无法识别的命令。输入 h 查看帮助。")
    return ("reveal", coord[0], coord[1])


# ====== 主循环 ======
HELP_TEXT = """
======== 帮助 ========
  揭开格子 :  输入坐标，如  a5
  标记地雷 :  在坐标前加 f，如  f a5  (再次输入可取消标记)
  重新开始 :  输入  r
  退出游戏 :  输入  q
  查看帮助 :  输入  h
======================
"""


def main():
    print("=" * 40)
    print("       欢迎来到控制台扫雷！")
    print(f"       棋盘: {ROWS} x {COLS}    地雷: {MINES}")
    print("=" * 40)
    print(HELP_TEXT)

    game = Minesweeper()
    game.render()

    while True:
        try:
            line = input("请输入命令> ")
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            return

        cmd = parse_command(line)
        action = cmd[0]

        if action == "invalid":
            print(f"⚠ {cmd[1]}")
            continue
        if action == "help":
            print(HELP_TEXT)
            continue
        if action == "quit":
            print("再见！")
            return
        if action == "restart":
            game.reset()
            print("✦ 已重新开始游戏。")
            game.render()
            continue

        if game.game_over:
            print("⚠ 游戏已结束，请输入 r 重新开始，或 q 退出。")
            continue

        if action == "flag":
            _, r, c = cmd
            ok = game.toggle_flag(r, c)
            if not ok:
                print("⚠ 该格子已揭开，无法标记。")
            game.render()
            continue

        if action == "reveal":
            _, r, c = cmd
            if game.flagged[r][c]:
                print("⚠ 该格子已被标记，请先取消标记再揭开。")
                continue
            hit_mine = game.reveal(r, c)
            game.render()
            if hit_mine:
                print("💥 砰！你踩到了地雷，游戏结束。")
                print("   输入 r 重新开始，或 q 退出。")
            elif game.won:
                print("🎉 恭喜你，成功扫除全部地雷，胜利！")
                print("   输入 r 重新开始，或 q 退出。")
            continue


if __name__ == "__main__":
    main()
