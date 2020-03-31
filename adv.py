from room import Room
from player import Player
from world import World
from util import Stack, Queue
from graph import Graph

import random
from ast import literal_eval

# Load world
world = World()


# You may uncomment the smaller graphs for development and testing purposes.
# map_file = "maps/test_line.txt"
# map_file = "maps/test_cross.txt"
# map_file = "maps/test_loop.txt"
# map_file = "maps/test_loop_fork.txt"
map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph = literal_eval(open(map_file, "r").read())
world.load_graph(room_graph)

# Print an ASCII map
world.print_rooms()

player = Player(world.starting_room)

# Fill this out with directions to walk
# traversal_path = ['n', 'n']
traversal_path = []


def traverseMaze(initialRoom):
    directions = {
        'n': 's',
        's': 'n',
        'w': 'e',
        'e': 'w',
    }
    # We initiate a Graph
    g = Graph()
    # We initiate a Stack for rooms
    s = Stack()
    # We initiate a Stack for directions
    d = Stack()
    # We create a visited List
    visited = list()
    # Push initial room to the stack
    s.push((None, None, initialRoom))
    # while the stack has something in it
    while s.size() > 0:
        # if visited list is less than the number of rooms
        if len(visited) < len(room_graph):
            # we pull the room at the head of the stack
            prev_room, inc_dir, room = s.pop()
            if room.id not in visited:
                visited.append(room.id)
            # print(f"We are in room {room.id}")
            # print(f"We have visited these rooms: {visited}")
            # if it is not in our map (Graph)
            if not room.id in g.vertices:
                # we add it to the Graph
                g.add_vertex(room.id)
                # we get all the exits and add them as "?" to the map
                exits = room.get_exits()
                for e in exits:
                    g.vertices[room.id][e] = "?"
            # if we are not in the initial room
            # print(g.vertices[room.id])
            if inc_dir != None:
                # connect current room with the previous room
                g.vertices[room.id][directions[inc_dir]] = prev_room.id
            # we pick one with ? at random
            av_exits = []
            for e in g.vertices[room.id]:
                if g.vertices[room.id][e] == "?":
                    av_exits.append(e)
            if len(av_exits) > 0:
                next_move = random.choice(av_exits)
                # we move in that direction
                player.travel(next_move)
                current_room = player.current_room
                # we add the direction to the stack of directions
                d.push(next_move)
                # we add direction to traversal path
                traversal_path.append(next_move)
                # we connect the next room with the one we come from
                g.vertices[room.id][next_move] = current_room.id
                # print(g.vertices[room.id], "<< next move")
                # we add that room to the Stack for rooms
                s.push((room, next_move, current_room))
            # otherwise:
            else:
                # we pop a direction from the direction Stack
                dir = d.pop()
                # we move in the opposite direction
                opp_dir = directions[dir]
                player.travel(opp_dir)
                current_room = player.current_room
                # we add the room in the Stack of rooms
                traversal_path.append(opp_dir)
                s.push((room, opp_dir, current_room))
        # otherwise
        else:
            # exit the function
            break


# TRAVERSAL TEST
traverseMaze(player.current_room)
visited_rooms = set()
player.current_room = world.starting_room
visited_rooms.add(player.current_room)

for move in traversal_path:
    player.travel(move)
    visited_rooms.add(player.current_room)

if len(visited_rooms) == len(room_graph):
    print(
        f"TESTS PASSED: {len(traversal_path)} moves, {len(visited_rooms)} rooms visited")
else:
    print("TESTS FAILED: INCOMPLETE TRAVERSAL")
    print(f"{len(room_graph) - len(visited_rooms)} unvisited rooms")


#######
# UNCOMMENT TO WALK AROUND
#######
player.current_room.print_room_description(player)
while True:
    cmds = input("-> ").lower().split(" ")
    if cmds[0] in ["n", "s", "e", "w"]:
        player.travel(cmds[0], True)
    elif cmds[0] == "q":
        break
    else:
        print("I did not understand that command.")
