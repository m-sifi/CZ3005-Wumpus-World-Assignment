
:- dynamic([
   agent_location/2,
   agent_orientation/1,
   agent_arrow/0,
   agent_actions/1,

   wumpus/2,
   confundus/2,
   tingle/2,
   glitter/2,
   stentch/2,

   visited/2,
   safe/2
]).

agent_actions([]).

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
%   has_arrow.

reborn :- 
    reposition([on, off, off, off, off, off]),
    retractall(agent_arrow),
    assertz(agent_arrow).

move(moveforward, [Confounded, Stench, Tingle, Glitter, Bump, Scream]) :-
    handle_percept([Confounded, Stench, Tingle, Glitter, Bump, Scream]),
    update_agent(Bump).

reposition(L) :- 
    retractall(agent_location(_, _)),
    retractall(agent_orientation(_)),

    retractall(visited(_, _)),
    retractall(wumpus(_, _)),
    retractall(confundus(_, _)),
    retractall(tingle(_, _)),
    retractall(glitter(_, _)),
    retractall(stench(_, _)),
    retractall(safe(_, _)),
    retractall(wall(_, _)),

    assertz(agent_location(0, 0)),
    assertz(agent_orientation(rnorth)),
    handle_percept(L),

    assertz(visited(0, 0)),
    assertz(safe(0, 0)).

safe_visited(X, Y) :-
    visited(X, Y),
    \+ wumpus(X, Y),
    \+ confundus(X, Y).

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

current(X, Y, D) :-
    agent_location(X, Y),
    agent_orientation(D).

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

isAdjacent(X,Y, XT, YT) :-
    (X =:= XT, Y =:= YT+1);
    (X =:= XT, Y =:= YT-1);
    (X =:= XT+1, Y =:= YT);
    (X =:= XT-1, Y =:= YT).

update_agent(on).
update_agent(off).

execute(moveforward, X, Y, rnorth, X1, Y1, _) :-
    X1 is X, 
    Y1 is Y + 1.

execute(moveforward, X, Y, rsouth, X1, Y1, _) :-
    X1 is X, 
    Y1 is Y - 1.

execute(moveforward, X, Y, reast, X1, Y1, _) :-
    X1 is X - 1, 
    Y1 is Y.

execute(moveforward, X, Y, rwest, X1, Y1, _) :-
    X1 is X + 1, 
    Y1 is Y.

execute(turnright, _, _, rnorth, _, _, D) :- D = reast.
execute(turnright, _, _, reast, _, _, D) :- D = rsouth.
execute(turnright, _, _, rsouth, _, _, D) :- D = rwest.
execute(turnright, _, _, rwest, _, _, D) :- D = rnorth.

execute(turnleft, _, _, rnorth, _, _, D) :- D = rwest.
execute(turnleft, _, _, reast, _, _, D) :- D = rsouth.
execute(turnleft, _, _, rsouth, _, _, D) :- D = reast.
execute(turnleft, _, _, rwest, _, _, D) :- D = rnorth.

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
    retractall(wumpus(_, _)),
    retractall(confundus(_, _)),
    retractall(tingle(_, _)),
    retractall(glitter(_, _)),
    retractall(stentch(_, _)),

    retractall(agent_location(_, _)),
    retractall(agent_orientation(_)),
    assertz(agent_location(0, 0)),
    assertz(agent_orientation(rnorth)).

confound(off).

% Stench Status
stench(on) :-
    agent_location(X, Y),
    XR is X + 1, assume_wumpus(on, XR, Y),
    XL is X - 1, assume_wumpus(on, XL, Y),
    YU is Y + 1, assume_wumpus(on, X, YU),
    YD is Y - 1, assume_wumpus(on, X, YD),
    true.

stench(off) :-
    agent_location(X, Y),
    XR is X + 1, assume_wumpus(off, XR, Y),
    XL is X - 1, assume_wumpus(off, XL, Y),
    YU is Y + 1, assume_wumpus(off, X, YU),
    YD is Y - 1, assume_wumpus(off, X, YD),
    true.

% Tingle Status
tingle(on) :-
    agent_location(X, Y),
    XR is X + 1, assume_portal(on, XR, Y),
    XL is X - 1, assume_portal(on, XL, Y),
    YU is Y + 1, assume_portal(on, X, YU),
    YD is Y - 1, assume_portal(on, X, YD),
    true.

tingle(off) :-
    agent_location(X, Y),
    XR is X + 1, assume_portal(off, XR, Y),
    XL is X - 1, assume_portal(off, XL, Y),
    YU is Y + 1, assume_portal(off, X, YU),
    YD is Y - 1, assume_portal(off, X, YD),
    true.

% Glitter Status
glitter(on) :-
    agent_location(X, Y),
    assertz(glitter(X, Y)).

glitter(off) :-
    agent_location(X, Y),
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
bump(on).
bump(off).

% Scream Status
scream(on).
scream(off).

assume_wumpus(on, X, Y) :- \+ visited(X, Y), assertz(wumpus(X, Y)).
assume_wumpus(off, X, Y) :- retractall(wumpus(X, Y)), assertz(safe(X, Y)).

assume_portal(on, X, Y) :- \+visited(X, Y), assertz(confundus(X, Y)).
assume_portal(off, X, Y) :- retractall(confundus(X, Y)), assertz(safe(X, Y)).

assume_glitter(on, X, Y) :- assertz(glitter(X, Y)).
assume_glitter(off, X, Y) :- retractall(glitter(X, Y)).

% 
% Utilities
%

distance(X1, Y1, X2, Y2, Distance) :-
    Distance is abs(X2 - X1) + abs(Y2 - Y1).

hash(X, Y, H) :-
    H is (X * 100) + Y.