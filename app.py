import streamlit as st
import chess
import random


def explain_move(move: chess.Move, board_before_move: chess.Board) -> str:
    """Provide a basic explanation for the piece moved."""
    piece = board_before_move.piece_at(move.from_square)
    piece_name = piece.symbol().upper() if piece else "未知"
    explanations = {
        "P": "兵的推进控制中心。",
        "N": "马出动控制关键格。",
        "B": "象牵制长对角线。",
        "R": "车的纵/横线控制。",
        "Q": "后出动要谨慎。",
        "K": "王要安全，避免暴露。",
    }
    return explanations.get(piece_name, "注意防守与中心控制。")


def run_app():
    """Run the chess teaching web application."""
    st.set_page_config(page_title="国际象棋教学对弈", layout="wide")
    st.title("♟️ 国际象棋教学对弈")
    st.markdown("与你的AI教练实时下棋、复盘与讲解。请输入走法例如 `e2e4`。")

    # Initialize or retrieve board state
    if "board" not in st.session_state:
        st.session_state.board = chess.Board()

    board = st.session_state.board

    # Layout columns: left for board, right for input and messages
    col1, col2 = st.columns([2, 1])

    with col1:
        st.image(board._repr_svg_(), use_column_width=True)

    # Input area for player move
    with col2:
        move_input = st.text_input("你的走法 (如 e2e4)：")
        if move_input:
            try:
                move = chess.Move.from_uci(move_input.strip())
                if move in board.legal_moves:
                    # Explain player's move
                    board_before = board.copy()
                    board.push(move)
                    st.success(f"你走了：{move.uci()} — 讲解：{explain_move(move, board_before)}")

                    # AI/Computer move if game not over
                    if not board.is_game_over():
                        ai_move = random.choice(list(board.legal_moves))
                        board.push(ai_move)
                        st.info(f"电脑走：{ai_move.uci()}")
                else:
                    st.error("非法走法，请重试。")
            except Exception:
                st.error("输入格式无效，请用标准 UCI 格式，例如 e2e4。")

    st.markdown("---")

    # Show result and move history if game is over
    if board.is_game_over():
        st.warning(f"棋局结束！结果：{board.result()}")
        st.markdown("### 复盘记录：")
        for i, mv in enumerate(board.move_stack):
            st.write(f"{i+1}. {mv.uci()}")


if __name__ == "__main__":
    run_app()
