import streamlit as st
import chess
import random

# Define piece values for basic evaluation
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}

# Mapping of piece symbols to unicode characters for display
UNICODE_PIECES = {
    'P': '♙', 'p': '♟',
    'R': '♖', 'r': '♜',
    'N': '♘', 'n': '♞',
    'B': '♗', 'b': '♝',
    'Q': '♕', 'q': '♛',
    'K': '♔', 'k': '♚',
}

def evaluate_board(state: chess.Board) -> int:
    """Evaluate the board from White's perspective.

    Positive values favour White, negative favour Black. A simple material
    count is used along with checkmate detection. Stalemate is neutral.
    """
    # Checkmate and stalemate detection
    if state.is_checkmate():
        return -9999 if state.turn else 9999
    if state.is_stalemate():
        return 0
    score = 0
    for piece_type, value in PIECE_VALUES.items():
        score += len(state.pieces(piece_type, chess.WHITE)) * value
        score -= len(state.pieces(piece_type, chess.BLACK)) * value
    return score


def minimax(state: chess.Board, depth: int, alpha: float, beta: float, maximizing_player: bool):
    """Perform a minimax search with alpha‑beta pruning.

    Returns a tuple (score, best_move).
    """
    if depth == 0 or state.is_game_over():
        return evaluate_board(state), None
    best_move = None
    if maximizing_player:
        max_eval = float('-inf')
        for move in state.legal_moves:
            state.push(move)
            eval_score, _ = minimax(state, depth - 1, alpha, beta, False)
            state.pop()
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in state.legal_moves:
            state.push(move)
            eval_score, _ = minimax(state, depth - 1, alpha, beta, True)
            state.pop()
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move


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
    """Run the chess teaching web application with an interactive board."""
    st.set_page_config(page_title="国际象棋教学对弈", layout="wide")
    st.title("♟️ 国际象棋教学对弈")
    st.markdown("点击棋子以选择它，再点击目标格子完成移动。AI 将基于简易算法进行回应并提供讲解。")

    # Initialize the chess board and selection state
    if "board" not in st.session_state:
        st.session_state.board = chess.Board()
    if "selected_square" not in st.session_state:
        st.session_state.selected_square = None

    board: chess.Board = st.session_state.board

    # Restart button to reset the game
    if st.button("重新开始一局"):
        st.session_state.board = chess.Board()
        st.session_state.selected_square = None
        board = st.session_state.board

    # Display status messages
    status_placeholder = st.empty()

    # Build the interactive board
    # Use columns to create an 8x8 grid; iterate ranks 8 to 1 (7 down to 0)
    clicked_square = None
    board_cols = st.columns(8)
    for rank in range(7, -1, -1):
        row_cols = st.columns(8)
        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            piece_symbol = piece.symbol() if piece else None
            label = UNICODE_PIECES.get(piece_symbol, " ")
            sq_name = chess.square_name(square)
            # Provide a unique key for each button
            if row_cols[file].button(label, key=f"{sq_name}_btn"):
                clicked_square = sq_name

    # Handle click logic after constructing the board so that session state is not modified mid‑render
    if clicked_square:
        selected = st.session_state.selected_square
        clicked_piece = board.piece_at(chess.parse_square(clicked_square))
        if selected is None:
            # First click: select a piece if it belongs to the player
            if clicked_piece and clicked_piece.color == chess.WHITE and board.turn:
                st.session_state.selected_square = clicked_square
                status_placeholder.info(f"已选择 {clicked_square}，请点击目标格子。")
            else:
                status_placeholder.warning("请选择你的棋子（白方）。")
        else:
            # Second click: attempt to move from selected to clicked_square
            move_uci = selected + clicked_square
            move = chess.Move.from_uci(move_uci)
            # Handle pawn promotion by defaulting to queen if necessary
            if move not in board.legal_moves:
                # Try queen promotion
                try:
                    move = chess.Move.from_uci(move_uci + 'q')
                except Exception:
                    pass
            if move in board.legal_moves:
                # Execute player's move
                board_before = board.copy()
                board.push(move)
                status_placeholder.success(f"你走了：{move.uci()} — 讲解：{explain_move(move, board_before)}")
                st.session_state.selected_square = None
                # If game continues, let AI respond
                if not board.is_game_over():
                    # Use minimax for AI decision making
                    _, ai_move = minimax(board, depth=2, alpha=float('-inf'), beta=float('inf'), maximizing_player=board.turn)
                    if ai_move:
                        ai_before = board.copy()
                        board.push(ai_move)
                        status_placeholder.info(f"电脑走：{ai_move.uci()} — 讲解：{explain_move(ai_move, ai_before)}")
            else:
                status_placeholder.error("非法走法，请重试。")
                st.session_state.selected_square = None

    st.markdown("---")

    # Display end of game results and move history
    if board.is_game_over():
        result_text = board.result()
        st.warning(f"棋局结束！结果：{result_text}")
        st.markdown("### 复盘记录：")
        for i, mv in enumerate(board.move_stack):
            st.write(f"{i+1}. {mv.uci()}")


if __name__ == "__main__":
    run_app()
