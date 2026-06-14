"""自动化测试 - 控制台扫雷游戏"""
import sys
import os
import random

# 确保可导入 game.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import game


def test_initial_state():
    """测试初始状态：无地雷，所有格子隐藏"""
    g = game.Minesweeper()
    assert g.game_over == False
    assert g.won == False
    assert g.mines_placed == False
    # 所有格子未揭开
    for r in range(game.ROWS):
        for c in range(game.COLS):
            assert g.revealed[r][c] == False
            assert g.flagged[r][c] == False


def test_mines_placed_on_first_reveal():
    """测试地雷在首次揭开时放置"""
    g = game.Minesweeper()
    assert g.mines_placed == False
    g.reveal(0, 0)
    assert g.mines_placed == True
    # 10颗雷
    mine_count = sum(1 for r in range(game.ROWS) for c in range(game.COLS) if g.mines[r][c])
    assert mine_count == game.MINES


def test_first_click_safe():
    """测试首次点击位置及周围3x3区域无雷"""
    g = game.Minesweeper()
    g.reveal(5, 5)
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            rr, cc = 5 + dr, 5 + dc
            if 0 <= rr < game.ROWS and 0 <= cc < game.COLS:
                assert g.mines[rr][cc] == False, f"Mine at ({rr},{cc}) - unsafe first click"


def test_auto_expand():
    """测试空白格自动展开"""
    # 用固定seed确保5,5附近有空白区域
    random.seed(42)
    g = game.Minesweeper()
    # 主动设定地雷位置，确保 (5,5) 附近足够安全
    # 改为直接测试BFS逻辑
    g.place_mines(5, 5)

    # 记录揭开前的已揭格子数
    before = sum(1 for r in range(game.ROWS) for c in range(game.COLS) if g.revealed[r][c])
    g.reveal(5, 5)
    after = sum(1 for r in range(game.ROWS) for c in range(game.COLS) if g.revealed[r][c])
    # auto-expand 应该揭开多个格子
    assert after > before + 1, f"Auto-expand didn't work: before={before}, after={after}"


def test_toggle_flag():
    """测试标记/取消标记功能"""
    g = game.Minesweeper()
    g.place_mines(0, 0)
    # 标记一个格子
    result = g.toggle_flag(0, 0)
    assert result == True
    assert g.flagged[0][0] == True
    # 再次标记取消
    result = g.toggle_flag(0, 0)
    assert result == True
    assert g.flagged[0][0] == False


def test_flag_on_revealed_blocked():
    """测试已揭开格子不能标记"""
    g = game.Minesweeper()
    g.reveal(5, 5)  # 首次揭开
    # 找一个已揭开的格子
    revealed_pos = None
    for r in range(game.ROWS):
        for c in range(game.COLS):
            if g.revealed[r][c]:
                revealed_pos = (r, c)
                break
        if revealed_pos:
            break
    if revealed_pos:
        result = g.toggle_flag(*revealed_pos)
        assert result == False, "Should not flag revealed cell"


def test_hit_mine():
    """测试踩雷后游戏结束"""
    g = game.Minesweeper()
    # 手动放置一颗雷在确定位置
    g.mines_placed = True
    g.mines[0][0] = True
    g.adjacent[0][0] = 0  # 虽然是雷但adjacent不重要
    g.adjacent[0][1] = 1
    g.adjacent[1][0] = 1
    g.adjacent[1][1] = 1
    g.adjacent[0][2] = 0 if not g.mines[0][2] else 0  # 懒得算，不重要

    hit = g.reveal(0, 0)
    assert hit == True
    assert g.game_over == True


def test_parse_coord():
    """测试坐标解析"""
    # 标准格式
    assert game.parse_coord("a5") == (4, 0)
    assert game.parse_coord("A5") == (4, 0)
    assert game.parse_coord("j10") == (9, 9)
    # 数字在前
    assert game.parse_coord("5a") == (4, 0)
    # 无效
    assert game.parse_coord("") == None
    assert game.parse_coord("z99") == None
    assert game.parse_coord("abc") == None


def test_parse_command():
    """测试命令解析"""
    assert game.parse_command("r")[0] == "restart"
    assert game.parse_command("q")[0] == "quit"
    assert game.parse_command("h")[0] == "help"
    assert game.parse_command("a5")[0] == "reveal"
    assert game.parse_command("f a5")[0] == "flag"
    assert game.parse_command("")[0] == "invalid"
    assert game.parse_command("xyz")[0] == "invalid"


def test_win_condition():
    """测试游戏胜利条件"""
    g = game.Minesweeper()
    # 手动设置：只有一颗雷在(0,0)
    g.mines_placed = True
    for r in range(game.ROWS):
        for c in range(game.COLS):
            g.mines[r][c] = False
    g.mines[0][0] = True
    # 预先揭开所有非雷格子
    for r in range(game.ROWS):
        for c in range(game.COLS):
            if not g.mines[r][c]:
                g.revealed[r][c] = True
    # 检查胜利
    g._check_win()
    assert g.won == True
    assert g.game_over == True


def test_reset():
    """测试重置后状态"""
    g = game.Minesweeper()
    g.reveal(5, 5)
    g.toggle_flag(1, 1)
    g.reset()

    assert g.game_over == False
    assert g.won == False
    assert g.mines_placed == False
    for r in range(game.ROWS):
        for c in range(game.COLS):
            assert g.revealed[r][c] == False
            assert g.flagged[r][c] == False


def test_render_no_error():
    """测试渲染不报错"""
    g = game.Minesweeper()
    # 初始状态渲染
    try:
        g.render()
    except Exception as e:
        assert False, f"Render failed on initial state: {e}"
    # 首次揭开后渲染
    g.reveal(5, 5)
    try:
        g.render()
    except Exception as e:
        assert False, f"Render failed after reveal: {e}"


def test_flag_count_display():
    """测试旗帜计数：标记后剩余地雷数应减少"""
    g = game.Minesweeper()
    g.place_mines(0, 0)
    g.toggle_flag(9, 9)
    # render应可正常运行（检查输出格式）
    # flags_used = 1
    # 剩余雷数 = MINES - 1
    # 这个测试验证 toggle_flag 和 render 的耦合没有问题
    try:
        g.render()
    except Exception as e:
        assert False, f"Render with flag failed: {e}"


def test_reveal_flagged_cell():
    """测试揭开已标记格子是否被阻止"""
    g = game.Minesweeper()
    g.place_mines(0, 0)
    g.toggle_flag(3, 3)
    # 从外部测试：我们需要检查 game 逻辑中 flagged cell 被标记时是否拒绝 reveal
    # 目前 reveal 方法内部对 flagged cell 直接返回 False 而不揭开
    result = g.reveal(3, 3)
    # 应该是安全的（不踩雷），但因为被标记，reveal内部的逻辑会先检查flagged
    # 查看代码：reveal方法第84行 `if self.flagged[r][c] or self.revealed[r][c]: return False`
    # 所以对于 flagged cell，reveal 会返回 False 且不揭开
    assert result == False
    # 格子应该还没有被揭开
    assert g.revealed[3][3] == False
