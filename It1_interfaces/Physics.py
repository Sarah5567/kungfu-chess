from typing import Tuple
from abc import ABC, abstractmethod
from weakref import finalize

from Command import Command
from Board import Board


class Physics(ABC):
    def __init__(self, start_cell: Tuple[int, int], board: Board, speed_m_s: float = 1.0):
        self.start_cell = start_cell
        self.board = board
        self.speed = speed_m_s * 100
        self.pos = self.board.cell_to_world(start_cell)  # (x, y) in meters
        self.start_time = 0
        self.cmd = None
        self.finished = False

    @abstractmethod
    def reset(self, cmd: Command):
        self.cmd = cmd
        self.start_time = 0  # will be set on first update

    @abstractmethod
    def update(self, now_ms: int) -> Command:
        pass

    @abstractmethod
    def can_be_captured(self) -> bool:
        pass

    @abstractmethod
    def can_capture(self) -> bool:
        pass

    def get_pos(self) -> Tuple[float, float]:
        return self.pos

    def get_pos_in_cell(self):
        return self.board.world_to_cell(self.pos)


class IdlePhysics(Physics):
    def reset(self, cmd: Command):
        super().reset(cmd)
        self.start_cell = tuple(cmd.params[0])
        self.pos = self.board.cell_to_world(self.start_cell)

    def update(self, now_ms: int) -> Command:
        return None

    def can_be_captured(self) -> bool:
        return True

    def can_capture(self) -> bool:
        return True


from typing import Tuple
from Command import Command
from Board import Board
from Physics import Physics


class MovePhysics(Physics):
    def __init__(self, start_cell: Tuple[int, int], board: Board, speed_m_s: float = 1.0):
        super().__init__(start_cell, board, speed_m_s)
        self.start_pos = self.board.cell_to_world(start_cell)
        self.end_pos = self.start_pos
        self.start_time = 0
        self.duration_ms = 1
        self.finished = False
        self.extra_delay_ms = 300  # Add 300ms after movement is finished

    def reset(self, cmd: Command):
        self.cmd = cmd
        self.finished = False
        self.start_cell = self.board.algebraic_to_cell(cmd.params[0])
        self.end_cell = self.board.algebraic_to_cell(cmd.params[1])
        self.start_pos = self.board.cell_to_world(self.start_cell)
        self.end_pos = self.board.cell_to_world(self.end_cell)
        self.pos = self.start_pos
        dist = ((self.end_pos[0] - self.start_pos[0]) ** 2 +
                (self.end_pos[1] - self.start_pos[1]) ** 2) ** 0.5
        # Calculate the required time based on distance and speed – movement part
        self.duration_ms = max(1, int((dist / self.speed) * 1000))
        # Total time including the delay after movement
        self.total_duration_ms = self.duration_ms + self.extra_delay_ms
        self.start_time = None

    def update(self, now_ms: int) -> Command:
        if self.finished:
            return self.cmd

        if self.start_time is None:
            self.start_time = now_ms

        elapsed = now_ms - self.start_time
        if elapsed < self.duration_ms:
            # Normal movement until destination – position updates linearly
            t = elapsed / self.duration_ms
            self.pos = (
                self.start_pos[0] + t * (self.end_pos[0] - self.start_pos[0]),
                self.start_pos[1] + t * (self.end_pos[1] - self.start_pos[1])
            )
        elif elapsed < self.total_duration_ms:
            self.pos = self.end_pos
        else:
            self.finished = True
            return self.cmd

        return None

    def can_be_captured(self) -> bool:
        return True

    def can_capture(self) -> bool:
        return True

    def get_pos(self) -> Tuple[int, int]:
        return self.pos


class JumpPhysics(Physics):
    def reset(self, cmd: Command):
        super().reset(cmd)
        self.jump_duration = 1000
        self.start_time = None
        self.start_cell = self.board.algebraic_to_cell(cmd.params[0])
        self.end_cell = self.board.algebraic_to_cell(cmd.params[1])
        self.pos = self.board.cell_to_world(self.end_cell)
    def update(self, now_ms: int) -> Command:
        if self.start_time is None:
            self.start_time = now_ms
        if now_ms - self.start_time >= self.jump_duration:
            self.finished = True
            return self.cmd
        return None
    def can_be_captured(self) -> bool:
        return False
    def can_capture(self) -> bool:
        return False

class ShortRestPhysics(Physics):
    def reset(self, cmd: Command):
        super().reset(cmd)
        self.rest_duration = 500  # half sec
        self.start_time = None
        self.start_cell = tuple(cmd.params[0])
        self.pos = self.board.cell_to_world(self.start_cell)
    def update(self, now_ms: int) -> Command:
        if self.start_time is None:
            self.start_time = now_ms
        if now_ms - self.start_time >= self.rest_duration:
            return Command(
                timestamp=now_ms,
                piece_id=self.cmd.piece_id,
                type="idle",
                params=[self.start_cell, self.start_cell]
            )
        return None
    def can_be_captured(self) -> bool:
        return True
    def can_capture(self) -> bool:
        return False

class LongRestPhysics(Physics):
    def reset(self, cmd: Command):
        super().reset(cmd)
        self.rest_duration = 1500  # 1.5 sec
        self.start_time = None
        self.start_cell = tuple(cmd.params[0])
        self.pos = self.board.cell_to_world(self.start_cell)

    def update(self, now_ms: int) -> Command:
        if self.start_time is None:
            self.start_time = now_ms

        # if now_ms - self.start_time >= self.rest_duration:
        #     return self.cmd

        if now_ms - self.start_time >= self.rest_duration:
            return Command(
                timestamp=now_ms,
                piece_id=self.cmd.piece_id,
                type="idle",
                params=[self.start_cell, self.start_cell]
            )
        return None

    def can_be_captured(self) -> bool:
        return True

    def can_capture(self) -> bool:
        return False