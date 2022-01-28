import graphviz
import chess
import IPython
from collections import defaultdict


class Node:
    def __init__(self, root=False):
        self.root = root
        self.nodes = defaultdict(Node)

        self.score = None
        self.white_turn = True
        self.principal_variation = False
        self.pruned = False

    def add_move(self, moves: list, whiteTurn: bool, score: int):
        self.white_turn = whiteTurn

        if not moves:
            self.score = score
            return

        self.nodes[moves[0]].add_move(moves[1:], not whiteTurn, score)

    def calculate_principal_variation(self):
        self.principal_variation = True

        for node in self.nodes.values():
            if self.root or self.score == node.score:
                node.calculate_principal_variation()

    def calculate_pruned_nodes(self, board: chess.Board):
        if not self.nodes:
            return

        for move, node in self.nodes.items():
            board.push(move)
            node.calculate_pruned_nodes(board)
            board.pop()

        for move in board.legal_moves:
            if move not in self.nodes:
                self.nodes[move].pruned = True

    def count_nodes(self):
        count = 0 if self.pruned else 1
        return count + sum(node.count_nodes() for node in self.nodes.values())

    def count_pruned(self):
        count = 1 if self.pruned else 0
        return count + sum(node.count_pruned() for node in self.nodes.values())

    def search(self, moves: list):
        if not moves:
            return self

        return self.nodes[moves[0]].search(moves[1:])


class MinMaxTree:
    def __init__(self):
        self.root_board = None
        self.root_board_length = None
        self.node = None

    def init(self, board):
        '''Init tree'''
        self.root_board = board.copy()
        self.root_board_length = len(self.root_board.move_stack)
        self.node = Node(root=True)

    def check_reset(self, board: chess.Board):
        '''Check if board should be resetted because a next depth is explored'''
        if len(board.move_stack) != len(self.root_board.move_stack) + 1:
            return

        if board.move_stack[-1] in self.node.nodes:
            self.node = Node(root=True)

    def add_move(self, board: chess.Board, score: int):
        '''Add move to the tree'''
        self.node.add_move(
            board.move_stack[self.root_board_length:],
            self.root_board.turn is chess.WHITE,
            score
        )

    def complete(self):
        '''Add some additional information to the tree after algorithm was completed'''
        self.node.calculate_principal_variation()
        self.node.calculate_pruned_nodes(self.root_board)

    def count(self):
        '''Count the number of visited nodes and pruned paths'''
        print("Tree Statistics")
        print(f"{self.node.count_nodes()} nodes visited")
        print(f"{self.node.count_pruned()} paths pruned")

    def draw(self, moves=[], depth: int = 10):
        MinMaxGraph(self.node.search(moves), depth).dislay()


class MinMaxGraph:
    def __init__(self, node: Node, depth: int):
        self.dot = graphviz.Digraph('Min Max graph')
        self.dot.attr(bgcolor="gray70")

        self._add_node_to_graph(node, depth)

    def dislay(self):
        IPython.display.display(self.dot)

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
        shape = "doublecircle" if node.principal_variation else "circle"

        if node.root:
            label = "root"
        elif node.pruned:
            label = "?"
        else:
            label = str(node.score)

        self.dot.node(
            f"{id(node)}",
            label,
            style='filled',
            color=color,
            fontcolor=font_color,
            shape=shape
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


def inject_value(tree: MinMaxTree, value_function, relative):
    def value(board: chess.Board, depth: int, *args, **kwargs):
        # TODO: Doesn't work for mdtf
        # tree.check_reset(board)

        score = value_function(board, depth, *args, **kwargs)

        if relative and board.turn is chess.BLACK:
            tree.add_move(board, -score)
        else:
            tree.add_move(board, score)
        return score

    return value


def inject_evaluate_moves(tree: MinMaxTree, evaluate_moves_function):
    def _evaluate_moves(board: chess.Board):
        tree.init(board)
        result = evaluate_moves_function(board)
        tree.complete()
        return result

    return _evaluate_moves


def add_tree_to_engine(engine, relative: bool = False):
    tree = MinMaxTree()
    engine._evaluate_moves = inject_evaluate_moves(tree, engine._evaluate_moves)
    engine._value = inject_value(tree, engine._value, relative)
    return tree