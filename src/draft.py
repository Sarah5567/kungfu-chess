Graphics = get curr images
Physics  = get curr pos
State    = Graphics + Physics + Transitions to other states
Piece    = ID + Moves + Wrapper for State (to hide state transitions)
Board    = background + pix / world dimensions
Game     = Pieces + Board + run() # game logic.

run()
    in = listen to keyboard
    process_input(in)
    
#design patterns:
# Factory, Command, Tempalte, State Machine

def create_game(board.txt, root_folder):
    pieces_templates = {} # { piece_id : piece }
    game_pieces = []
    board = read_board(board.txt)
    
    for piece_id, location in board:
        if piece_id not in pieces_templates:
            pieces_templates[piece_id] = create_piece(piece_id, root_folder, board)
        
        p = pieces_templates[piece_id].clone()
        p.set_location(location)
        game_pieces.append(p)
        
        # game_pieces.append(create_piece(piece_id, root_folder))
    
    game = Game(game_pieces, board)
    
    return game
      
def create_piece(piece_id = "QW", root_folder, board):
    folder = root_folder / piece_id
    moves = Moves(folder / "moves.txt", (board.H_cells, board.W_cells))
    states = {} # state name -> state
    states_folder = folder / "states"
    for subfolder in states_folder:
        state_name = subfolder.name
        cfg_path = subfolder / "config.json"
        cfg = read_config(cfg_path)
        physics = create_physics(state_name, cfg.physics)
        graphics = create_graphics(subfolder / "sprites", cfg.graphics)
        
        states[state_name] = State(graphics, physics)
    
    state["idle"].add_transition("move", state["move"])
    state["idle"].add_transition("jump", state["jump"])
    
    state["move"].add_transition("long_rest", state["long_rest"])
    state["jump"].add_transition("short_rest", state["short_rest"])
    
    state["long_rest"].add_transition("idle", state["idle"])
    state["short_rest"].add_transition("idle", state["idle"])
    
    return Piece(piece_id, state["idle"])
    
def create_physics(state_name, cfg.physics):
    switch state_name:
    case "idle" : return IdlePhysics(cfg.physics)
    case "move" : return MovePhysics(cfg.physics)
    ...
    
def create_graphics(sprites_folder, cfg.graphics):
    sprites = [] # read sprites from folder... 
    # ... init members by config... 
        
def main()
    game = create_game(...)
    game.run()
    
    
    
def test_WhenScenario_ThenResult():

def test_WhenInvalidInput_ThenRaiseException():
    ... 

def test_WhenMoveUpdate():
    # Arrange
    p = MovePhysics(...)
    p.reset(0)
    ..
    expected = [1.5,2.3]
    
    # Act
    p.update(5)
    
    # Assert
    actual = p.get_pos()
    assert actual == expected

# GPT: implement .... and create tests files using <pytest / JUnit / ... > 
# write tests divided into Arrange Act Assert and give meaningful test names
# make sure to cover both sanity and edge cases (invalid input etc.)
class FakePhysics(Physics):
    ...

# state_test.py
def test_WhenPhysicsOver_ThenTransitionState():
    # Arrange
    p = FakePhysics(...) # Mock or Fake object for testing
    g = FakeGraphics(...)
    
    # Dependency Injection
    s = State(p, g)
    ...
    for (i = 1 ... 5)
        new_s = s.update(i)
    assert new_s == s
    
    # Act
    new_s = s.update(6)
    
    # Assert
    assert new_s != s
    assert new_s.name == "something"
