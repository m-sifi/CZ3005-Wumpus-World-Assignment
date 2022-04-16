
:- dynamic([
    hasarrow/0,

    wumpus/2,
    confundus/2,
    tingle/2,
    glitter/2,
    stentch/2,

    current/3,
    visited/2,
    wall/2
]).

% Lab Predicates required to implement
%   reborn
%   move(Action, [Confounded, Stench, Tingle, Glitter, Bump, Scream])
%   reposition([Confounded, Stench, Tingle, Glitter, Bump, Scream])
%   
%  Localisation and Mapping
%   visited(X, Y) 
%   wumpus(X, Y) 
%   confundus(X, Y) 
%   tingle(X, Y) 
%   glitter(X, Y) 
%   stench(X, Y) 
%   safe(X, Y) 
%   wall(X ,Y)
%
%   explore(L)
%   current(X, Y, D)
%   hasarrow.

reborn :- 
    reposition([on, off, off, off, off, off]),
    retractall(agent_arrow),
    assertz(agent_arrow).

move(moveforward, [Confounded, Stench, Tingle, Glitter, Bump, Scream]) :-
    update_agent(Bump),
    handle_percept([Confounded, Stench, Tingle, Glitter, Bump, Scream]).

move(shoot, [Confounded, Stench, Tingle, Glitter, Bump, Scream]) :-
    retractall(hasarrow),
    handle_percept([Confounded, Stench, Tingle, Glitter, Bump, Scream]).

move(pickup, [Confounded, Stench, Tingle, Glitter, Bump, Scream]) :-
    current(X, Y, _),
    glitter(X, Y),
    retractall(glitter(X, Y)),
    handle_percept([Confounded, Stench, Tingle, Glitter, Bump, Scream]).

move(turnleft, _) :-
    current(X, Y, D),
    execute(turnleft, X, Y, D, _, _, D1),
    retractall(current(_, _, _)),
    assertz(current(X, Y, D1)).

move(turnright, _) :-
    current(X, Y, D),
    execute(turnright, X, Y, D, _, _, D1),
    retractall(current(_, _, _)),
    assertz(current(X, Y, D1)).

reposition(L) :- 
    handle_percept(L).

safe(X, Y) :-
    \+ wumpus(X, Y),
    \+ confundus(X, Y),
    \+ wall(X, Y).

% explore(L) where L = Actions that lead agent to safe unvisited area. 
%

% explore(L) :- distinct(explore(L)).

explore(L) :-
    % Placeholder Implementation
    current(X, Y, D),
    explore(X, Y, D, L, []).

explore(X, Y, D, [PossibleAction|L], Visited) :-
    hash(X, Y, H),
    \+ member(H, Visited),
    possible(L, PossibleAction),
    execute(PossibleAction, X, Y, D, X0, Y0, D0),
    ( 
        safe(X0, Y0), visited(X0, Y0),
        explore(X0, Y0, D0, L, [H|Visited])
    ;
        safe(X0, Y0), not(visited(X0, Y0))
    ).

% explore(L) :-
%     % Placeholder Implementation
%     \+ any_unexplored,
%     \+ glitter(_, _),
%     current(0, 0, _),
%     append([], [], L).

% For naming consistency sake, hasarrow is an alias for agent_arrow.
hasarrow :- agent_arrow.

%
% Exploring
%

possible([], moveforward).
possible([moveforward| L], turnleft).
possible([moveforward| L], turnright).
possible([moveforward| L], moveforward).
possible([turnleft| L], moveforward).
possible([turnright| L], moveforward).
possible(_, moveforward).

% 
% Mapping 
%

update_agent(on) :-
    current(X, Y, D),
    execute(moveforward, X, Y, D, X1, Y1, _),
    assertz(wall(X1, Y1)).

update_agent(off) :-
    current(X, Y, D),
    execute(moveforward, X, Y, D, X1, Y1, _),
    retractall(current(_, _, _)),
    assertz(current(X1, Y1, D)),
    assertz(visited(X1, Y1)).

execute(moveforward, X, Y, rnorth, X1, Y1, _) :-
    X1 is X, 
    Y1 is Y + 1.

execute(moveforward, X, Y, rsouth, X1, Y1, _) :-
    X1 is X, 
    Y1 is Y - 1.

execute(moveforward, X, Y, reast, X1, Y1, _) :-
    X1 is X + 1, 
    Y1 is Y.

execute(moveforward, X, Y, rwest, X1, Y1, _) :-
    X1 is X - 1, 
    Y1 is Y.

execute(turnright, _, _, rnorth, _, _, D) :- D = reast.
execute(turnright, _, _, reast, _, _, D) :- D = rsouth.
execute(turnright, _, _, rsouth, _, _, D) :- D = rwest.
execute(turnright, _, _, rwest, _, _, D) :- D = rnorth.

execute(turnleft, _, _, rnorth, _, _, D) :- D = rwest.
execute(turnleft, _, _, rwest, _, _, D) :- D = rsouth.
execute(turnleft, _, _, rsouth, _, _, D) :- D = reast.
execute(turnleft, _, _, reast, _, _, D) :- D = rnorth.

% 
% Perceptors Handler
% 

handle_percept([Confounded, Stench, Tingle, Glitter, Bump, Scream]) :-
    confound(Confounded),
    stench(Stench),
    tingle(Tingle),
    glitter(Glitter),
    bump(Bump),
    scream(Scream).

% Confounded Status
confound(on) :-
    retractall(current(_, _, _)),
    retractall(visited(_, _)),
    retractall(wumpus(_, _)),
    retractall(confundus(_, _)),
    retractall(tingle(_, _)),
    retractall(glitter(_, _)),
    retractall(stench(_, _)),
    retractall(wall(_, _)),

    assertz(current(0, 0, rnorth)),
    assertz(visited(0, 0)).

confound(off).

% Stench Status
stench(on) :-
    current(X, Y, _),
    assertz(stench(X, Y)),
    XR is X + 1, assume_wumpus(on, XR, Y),
    XL is X - 1, assume_wumpus(on, XL, Y),
    YU is Y + 1, assume_wumpus(on, X, YU),
    YD is Y - 1, assume_wumpus(on, X, YD).

stench(off) :-
    current(X, Y, _),
    retractall(stench(X, Y)),
    XR is X + 1, assume_wumpus(off, XR, Y),
    XL is X - 1, assume_wumpus(off, XL, Y),
    YU is Y + 1, assume_wumpus(off, X, YU),
    YD is Y - 1, assume_wumpus(off, X, YD).

% Tingle Status
tingle(on) :-
    current(X, Y, _),
    assertz(tingle(X, Y)),
    XR is X + 1, assume_portal(on, XR, Y),
    XL is X - 1, assume_portal(on, XL, Y),
    YU is Y + 1, assume_portal(on, X, YU),
    YD is Y - 1, assume_portal(on, X, YD).

tingle(off) :-
    current(X, Y, _),
    retractall(tingle(X, Y)),
    XR is X + 1, assume_portal(off, XR, Y),
    XL is X - 1, assume_portal(off, XL, Y),
    YU is Y + 1, assume_portal(off, X, YU),
    YD is Y - 1, assume_portal(off, X, YD).

% Glitter Status
glitter(on) :-
    current(X, Y, _),
    assertz(glitter(X, Y)).

glitter(off) :-
    current(X, Y, _),
    retractall(glitter(X, Y)).

% Bump Status
% bump(on) :-
%     % [TODO] Fail predicate so move(moveforward) don't run.
%     current(X, Y, D),
%     forward(X, Y, D, WX, WY),
%     assertz(wall(WX, WY)).

% bump(off) :-
%     current(X, Y, D),
%     forward(X, Y, D, WX, WY),
%     retractall(wall(WX, WY)).

bump(on) :-
    current(X, Y, D),
    execute(moveforward, X, Y, D, X1, Y1, _),
    assertz(wall(X1, Y1)).

bump(off).

% Scream Status
scream(on) :- retractall(wumpus(_, _)).
scream(off).

assume_wumpus(on, X, Y) :- assertz(wumpus(X, Y)).
assume_wumpus(off, X, Y) :- retractall(wumpus(X, Y)).

assume_portal(on, X, Y) :- assertz(confundus(X, Y)).
assume_portal(off, X, Y) :- retractall(confundus(X, Y)).

assume_glitter(on, X, Y) :- assertz(glitter(X, Y)).
assume_glitter(off, X, Y) :- retractall(glitter(X, Y)).

% 
% Utilities
%

distance(X1, Y1, X2, Y2, Distance) :-
    Distance is abs(X2 - X1) + abs(Y2 - Y1).

hash(X, Y, H) :-
    H is (X * 100) + Y.