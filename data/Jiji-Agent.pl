
:- dynamic([
    hasarrow/0,

    wumpus/2,
    confundus/2,
    tingle/2,
    glitter/2,
    stench/2,
    safe/2,

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
    retractall(hasarrow),
    assertz(hasarrow).

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

%
% Planning
%

safe_visited(X, Y) :-
    safe(X, Y),
    visited(X, Y),
    \+ wall(X, Y),
    \+ wumpus(X, Y),
    \+ confundus(X, Y).

safe_unvisited(X, Y) :-
    safe(X, Y),
    \+ visited(X, Y),
    \+ wall(X, Y).

flatten2([], []) :- !.
flatten2([L|Ls], FlatL) :-
    !,
    flatten2(L, NewL),
    flatten2(Ls, NewLs),
    append(NewL, NewLs, FlatL).
flatten2(L, [L]).

explore(L) :-
    current(X, Y, D),
    explore_r(X, Y, D, [], L0),
    flatten2(L0, L).

explore_r(0, 0, D, Visited, []) :-
    aggregate_all(count, safe_unvisited(_, _), 0),
    aggregate_all(count, glitter(_, _), 0), !.

explore_r(X, Y, D, Visited, []) :-
    aggregate_all(count, safe_unvisited(_, _), Count),
    safe_unvisited(X, Y), !.

% explore_r(Count, X, Y, D, Visited, []) :-
%     not((safe(X, Y), \+ visited(X, Y), \+ wall(X, Y))),
%     findall(1, glitter(A, B), L),
%     length(L, 0),
%     X == 0,
%     Y == 0, !.

explore_r(X, Y, D, Visited, Path) :-
    \+ memberchk((X, Y), Visited),
    safe_visited(X, Y),
    glitter(X, Y),
    explore_move(X, Y, D, [(X, Y)|Visited], [pickup, Path]).

explore_r(X, Y, D, Visited, Path) :-
    \+ memberchk((X, Y), Visited),
    safe_visited(X, Y),
    explore_move(X, Y, D, [(X, Y)|Visited], Path).

explore_move(X, Y, D, Visited, [Actions, moveforward |Path]) :-
    face_north(X, Y, D, Actions),
    execute(moveforward, X, Y, rnorth, X1, Y1, D1),
    explore_r(X1, Y1, D1, Visited, Path).

explore_move(X, Y, D, Visited, [Actions, moveforward |Path]) :-
    face_east(X, Y, D, Actions),
    execute(moveforward, X, Y, reast, X1, Y1, D1),
    explore_r(X1, Y1, D1, Visited, Path).

explore_move(X, Y, D, Visited, [Actions, moveforward |Path]) :-
    face_south(X, Y, D, Actions),
    execute(moveforward, X, Y, rsouth, X1, Y1, D1),
    explore_r(X1, Y1, D1, Visited, Path).

explore_move(X, Y, D, Visited, [Actions, moveforward |Path]) :-
    face_west(X, Y, D, Actions),
    execute(moveforward, X, Y, rwest, X1, Y1, D1),
    explore_r(X1, Y1, D1, Visited, Path).

% explore_move(X, Y, D, Visited, [turnleft|Path]) :-
%     execute(turnleft, X, Y, D, X1, Y1, D1),
%     explore_r(X1, Y1, D1, Visited, Path).

% Optimise Face North

face_north(X, Y, rnorth, []) :- !.

face_north(X, Y, D, Actions) :-
    face_north_r(X, Y, D, L),
    length(L, 3),
    Actions = [turnleft].

face_north(X, Y, D, Actions) :-
    face_north_r(X, Y, D, Actions).

face_north_r(X, Y, D, [turnright|Actions]) :-
    execute(turnright, X, Y, D, _, _, D1),
    face_north(X, Y, D1, Actions).

% Optimise Face East

face_east(X, Y, reast, []) :- !.

face_east(X, Y, D, Actions) :-
    face_east_r(X, Y, D, L),
    length(L, 3),
    Actions = [turnleft].

face_east(X, Y, D, Actions) :-
    face_east_r(X, Y, D, Actions).

face_east_r(X, Y, D, [turnright|Actions]) :-
    execute(turnright, X, Y, D, _, _, D1),
    face_east(X, Y, D1, Actions).

% Optimise Face South

face_south(X, Y, rsouth, []) :- !.

face_south(X, Y, D, Actions) :-
    face_south_r(X, Y, D, L),
    length(L, 3),
    Actions = [turnleft].

face_south(X, Y, D, Actions) :-
    face_south_r(X, Y, D, Actions).

face_south_r(X, Y, D, [turnright|Actions]) :-
    execute(turnright, X, Y, D, _, _, D1),
    face_south(X, Y, D1, Actions).

% Optimise Face West

face_west(X, Y, rwest, []) :- !.

face_west(X, Y, D, Actions) :-
    face_west_r(X, Y, D, L),
    length(L, 3),
    Actions = [turnleft].

face_west(X, Y, D, Actions) :-
    face_west_r(X, Y, D, Actions).

face_west_r(X, Y, D, [turnright|Actions]) :-
    execute(turnright, X, Y, D, _, _, D1),
    face_west(X, Y, D1, Actions).

% 
% Mapping 
%

update_agent(on) :-
    current(X, Y, D),
    execute(moveforward, X, Y, D, X1, Y1, _),
    retractall(safe(X1, Y1)),
    
    % retractall(visited(X, Y)),
    assertz(visited(X, Y)),

    retractall(wall(X1, Y1)),
    assertz(wall(X1, Y1)).

update_agent(off) :-
    current(X, Y, D),
    execute(moveforward, X, Y, D, X1, Y1, _),
    retractall(current(_, _, _)),
    assertz(current(X1, Y1, D)),
    
    retractall(safe(X1, Y1)),
    assertz(safe(X1, Y1)),
    
    retractall(visited(X1, Y1)),
    assertz(visited(X1, Y1)).

execute(moveforward, X, Y, rnorth, X1, Y1, rnorth) :-
    X1 is X, 
    Y1 is Y + 1.

execute(moveforward, X, Y, rsouth, X1, Y1, rsouth) :-
    X1 is X, 
    Y1 is Y - 1.

execute(moveforward, X, Y, reast, X1, Y1, reast) :-
    X1 is X + 1, 
    Y1 is Y.

execute(moveforward, X, Y, rwest, X1, Y1, rwest) :-
    X1 is X - 1, 
    Y1 is Y.

execute(turnright, X, Y, rnorth, X, Y, reast).
execute(turnright, X, Y, reast, X, Y, rsouth).
execute(turnright, X, Y, rsouth, X, Y, rwest).
execute(turnright, X, Y, rwest, X, Y, rnorth).

execute(turnleft, X, Y, rnorth, X, Y, rwest).
execute(turnleft, X, Y, rwest, X, Y, rsouth).
execute(turnleft, X, Y, rsouth, X, Y, reast).
execute(turnleft, X, Y, reast, X, Y, rnorth).

% 
% Perceptors Handler
% 

handle_percept([Confounded, Stench, Tingle, Glitter, Bump, Scream]) :-
    confound(Confounded),
    stench(Stench),
    tingle(Tingle),
    glitter(Glitter),
    bump(Bump),
    scream(Scream),
    update_map.

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
    retractall(safe(_, _)),
    
    assertz(safe(0, 0)),
    assertz(current(0, 0, rnorth)),
    assertz(visited(0, 0)).

confound(off).

% Stench Status
stench(on) :-
    current(X, Y, _),
    retractall(stench(X, Y)), assertz(stench(X, Y)),
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
    retractall(tingle(X, Y)), assertz(tingle(X, Y)),
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
    retractall(glitter(X, Y)),  assertz(glitter(X, Y)).

glitter(off) :-
    current(X, Y, _),
    retractall(glitter(X, Y)).

bump(on) :-
    current(X, Y, D),
    execute(moveforward, X, Y, D, X1, Y1, _),
    retractall(safe(X1, Y1)),
    retractall(wall(X1, Y1)), assertz(wall(X1, Y1)).

bump(off).

% Scream Status
scream(on) :- retractall(wumpus(_, _)).
scream(off).

% assume_wumpus(on, X, Y) :- visited(X, Y), safe(X, Y).
% assume_wumpus(on, X, Y) :- \+ visited(X, Y), \+ safe(X, Y), retractall(wumpus(X, Y)), assertz(wumpus(X, Y)).
% assume_wumpus(off, X, Y) :- retractall(wumpus(X, Y)), retractall(safe(X,Y)), assertz(safe(X,Y)).

% assume_portal(on, X, Y) :- visited(X, Y), safe(X, Y).
% assume_portal(on, X, Y) :- \+ visited(X, Y), \+ safe(X, Y),(retractall(confundus(X, Y)), assertz(confundus(X, Y))).
% assume_portal(off, X, Y) :- retractall(confundus(X, Y)), retractall(safe(X,Y)), assertz(safe(X,Y)).


assume_wumpus(on, X, Y) :- retractall(wumpus(X, Y)), assertz(wumpus(X, Y)).
assume_wumpus(off, X, Y) :- retractall(wumpus(X, Y)), retractall(safe(X, Y)), assertz(safe(X, Y)). 

assume_portal(on, X, Y) :- retractall(confundus(X, Y)), assertz(confundus(X, Y)).
assume_portal(off, X, Y) :- retractall(confundus(X, Y)), retractall(safe(X, Y)), assertz(safe(X, Y)). 

assume_glitter(on, X, Y) :- assertz(glitter(X, Y)).
assume_glitter(off, X, Y) :- retractall(glitter(X, Y)).

update_map :-
    correct_visited,
    correct_safe.
    % correct_confundus_safe,
    % correct_wumpus_safe.

correct_safe :-
    safe(X, Y),
    wumpus(X, Y) ; confundus(X, Y),
    retractall(safe(X, Y)).

correct_safe.

correct_wumpus_safe :-
    safe(X, Y),
    wumpus(X, Y),
    retractall(safe(X, Y)).

correct_confundus_safe :-
    safe(X, Y),
    confundus(X, Y),
    retractall(safe(X, Y)).

correct_visited :-
    visited(X, Y),
    retractall(wumpus(X, Y)),
    retractall(confundus(X, Y)),
    retractall(safe(X, Y)),
    assertz(safe(X, Y)).
    
hash(X, Y, H) :- H is (X * 100) + Y.