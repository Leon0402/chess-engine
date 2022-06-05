import chess

board = chess.Board("r1bqrnk1/pp2bp1p/2p2p2/3p4/3P4/2NBPN2/PPQ2PPP/R4RK1 w - - 0 12")
board.move_stack = [chess.Move.from_uci('g5f6'), chess.Move.from_uci('g7f6')]
board.remove_piece_at(chess.D3)
print(board.move_stack)