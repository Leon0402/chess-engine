from collections import defaultdict

import graphviz
import chess
import IPython

from chess.engine import PovScore, Score


class Node:
    """TODO"""
    def __init__(self, root=False):
        self.root = root
        self.nodes = defaultdict(Node)

        self.score = None
        self.depth = None
        self.alpha = None
        self.beta = None

        self.quiesce = False
        self.white_turn = True
        self.principal_variation = False
        self.pruned = False

    def add_move(
        self,
        moves: list,
        white_turn: bool,
        score: int,
        depth: int,
        alpha: int,
        beta: int,
        quiesce: bool
    ):
        """TODO"""
        self.white_turn = white_turn

        if not moves:
            self.score = score
            self.depth = depth
            self.alpha = alpha
            self.beta = beta
            self.quiesce = quiesce
            return

        self.nodes[moves[0]].add_move(
            moves[1:], not white_turn, score, depth, alpha, beta, quiesce
        )

    def calculate_principal_variation(self):
        """TODO"""
        self.principal_variation = True

        for node in self.nodes.values():
            if self.root or self.score.white() == node.score.white():
                node.calculate_principal_variation()

    def calculate_pruned_nodes(self, board: chess.Board):
        """TODO"""
        if not self.nodes:
            return

        for move, node in self.nodes.items():
            board.push(move)
            node.calculate_pruned_nodes(board)
            board.pop()

        for move in board.legal_moves:
            if move not in self.nodes:
                self.nodes[move].pruned = True
                if self.quiesce:
                    self.nodes[move].quiesce = True

    def count_nodes(self):
        """TODO"""
        count = 1 if not self.pruned and not self.quiesce else 0
        return count + sum(node.count_nodes() for node in self.nodes.values())

    def count_pruned(self):
        """TODO"""
        count = 1 if self.pruned and not self.quiesce else 0
        return count + sum(node.count_pruned() for node in self.nodes.values())

    def count_quiesce_nodes(self):
        """TODO"""
        count = 1 if not self.pruned and self.quiesce else 1
        return count + sum(
            node.count_quiesce_nodes() for node in self.nodes.values()
        )

    def count_quiesce_pruned(self):
        """TODO"""
        count = 1 if self.pruned and self.quiesce else 0
        return count + sum(
            node.count_quiesce_pruned() for node in self.nodes.values()
        )

    def search(self, moves: list):
        """TODO"""
        if not moves:
            return self

        return self.nodes[moves[0]].search(moves[1:])


class MinMaxTree:
    """TODO"""
    def __init__(self):
        self.root_board = None
        self.root_board_length = None
        self.node = None
        self.last_depth = None

    def init(self, board):
        '''Init tree'''
        self.root_board = board.copy()
        self.root_board_length = len(self.root_board.move_stack)
        self.node = Node(root=True)
        self.last_depth = 0

    def check_reset(self, board: chess.Board, depth: int):
        '''Check if board should be resetted because a next depth is explored'''
        if len(board.move_stack) != len(self.root_board.move_stack) + 1:
            return

        if board.move_stack[-1] in self.node.nodes and depth > self.last_depth:
            self.node = Node(root=True)
            self.last_depth = depth

    def add_move(
        self,
        board: chess.Board,
        score: int,
        depth: int,
        alpha: int,
        beta: int,
        quiesce: bool = False
    ):
        '''Add move to the tree'''
        self.node.add_move(
            board.move_stack[self.root_board_length:],
            self.root_board.turn is chess.WHITE,
            score,
            depth,
            alpha,
            beta,
            quiesce
        )

    def complete(self):
        '''Add some additional information to the tree after algorithm was completed'''
        self.node.calculate_principal_variation()
        self.node.calculate_pruned_nodes(self.root_board)

    def count(self, quiesce: bool = False):
        '''Count the number of visited nodes and pruned paths'''
        print("Tree Statistics")
        print(f"{self.node.count_nodes()} nodes visited")
        print(f"{self.node.count_pruned()} paths pruned")
        if quiesce:
            print(f"{self.node.count_quiesce_nodes()} quiesce nodes visited")
            print(f"{self.node.count_quiesce_pruned()} quiesce paths pruned")

    def draw(self, moves=[], depth: int = 10):
        """TODO"""
        MinMaxGraph(self.node.search(moves), depth).dislay()

    def save(self, moves=[], depth: int = 10):
        """TODO"""
        MinMaxGraph(self.node.search(moves), depth).save()


class MinMaxGraph:
    """TODO"""
    def __init__(self, node: Node, depth: int):
        self.dot = graphviz.Digraph('Min Max graph')
        self.dot.attr(bgcolor="gray70")

        self._add_node_to_graph(node, depth)

    def dislay(self):
        """TODO"""
        IPython.display.display(self.dot)

    def save(self):
        """TODO"""
        self.dot.render(format="svg")

    def _add_node_to_graph(self, node, depth: int):
        self._insert_node(node)

        if depth == 0:
            return

        for move, next_node in node.nodes.items():
            self._add_node_to_graph(next_node, depth - 1)
            self._insert_edge(node, move, next_node)

    def _insert_node(self, node):
        color = "white" if node.white_turn else "black"
        font_color = "black" if node.white_turn else "white"

        if node.nodes:
            shape = "doublecircle" if node.principal_variation else "circle"
        else:
            shape = "doubleoctagon" if node.principal_variation else "octagon"

        if node.root:
            label = "root"
        elif node.pruned:
            label = "?"
        else:
            label = str(node.score.white())

        if node.alpha is not None:
            tooltip = f"alpha = {node.alpha}, beta = {node.beta}, depth = {node.depth}"
        else:
            tooltip = ""

        self.dot.node(
            f"{id(node)}",
            label,
            style='filled',
            color=color,
            fontcolor=font_color,
            shape=shape,
            tooltip=tooltip
        )

    def _insert_edge(self, prev_node: Node, move: chess.Move, next_node: Node):
        color = "white" if prev_node.white_turn else "black"

        self.dot.edge(
            f"{id(prev_node)}",
            f"{id(next_node)}",
            constraint='true',
            color=color,
            fontcolor=color,
            label=move.uci()
        )


def inject_quiescence(tree: MinMaxTree, quiesce_function):
    """TODO"""
    # Check for recursive calls and only in these cases add the move to the tree
    depth = 0

    def _quiescence(board: chess.Board, alpha: int, beta: int):
        nonlocal depth
        depth -= 1

        score = quiesce_function(board, alpha, beta)
        tree.add_move(board, score, depth, alpha, beta, quiesce=True)

        depth = 0

        return score

    return _quiescence


def inject_value(tree: MinMaxTree, value_function):
    """TODO"""
    def value(
        board: chess.Board,
        depth: int,
        alpha: Score = None,
        beta: Score = None,
    ):
        tree.check_reset(board, depth)

        if alpha is None:
            score = value_function(board, depth)
        else:
            score = value_function(board, depth, alpha, beta)

        tree.add_move(board, score, depth, alpha, beta)
        return score

    return value


def inject_evaluate_moves(tree: MinMaxTree, evaluate_moves_function):
    """TODO"""
    def _evaluate_moves(board: chess.Board):
        tree.init(board)
        result = evaluate_moves_function(board)
        tree.complete()
        return result

    return _evaluate_moves

def inject_find_best_move(tree: MinMaxTree, _find_best_move_function):
    """TODO"""
    def _find_best_move(board: chess.Board):
        tree.init(board)
        result = _find_best_move_function(board)
        tree.complete()
        return result

    return _find_best_move


def add_tree_to_engine(engine):
    """TODO"""
    tree = MinMaxTree()
    engine._evaluate_moves = inject_evaluate_moves(tree, engine._evaluate_moves)
    engine._value = inject_value(tree, engine._value)
    if hasattr(engine, "_quiescence"):
        engine._quiescence = inject_quiescence(tree, engine._quiescence)
    if hasattr(engine, "_find_best_move"):
        engine._find_best_move = inject_find_best_move(tree, engine._find_best_move)
    return tree