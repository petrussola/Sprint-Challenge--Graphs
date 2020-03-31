from room import Room
from player import Player
from world import World
from util import Stack
from graph import Graph

import random
from ast import literal_eval

# Load world
world = World()


# You may uncomment the smaller graphs for development and testing purposes.
# map_file = "maps/test_line.txt"
# map_file = "maps/test_cross.txt"
# map_file = "maps/test_loop.txt"
map_file = "maps/test_loop_fork.txt"
# map_file = "maps/main_maze.txt"

# Loads the map into a dictionary
room_graph = literal_eval(open(map_file, "r").read())
# print(room_graph, "<<<<<<<")
world.load_graph(room_graph)

# Print an ASCII map
world.print_rooms()

player = Player(world.starting_room)

# Fill this out with directions to walk
# traversal_path = ['n', 'n']
traversal_path = []


def get_random_direction(available_directions, current_room):
    # sometime we get available directions to be an empty array because we have explored all that we want to try, whether we are going forward (unexplored_dir) or backwards(explored_dir)
    # if there are available direction
    if len(available_directions) > 0:
        # we get a random unexplored direction
        numb = random.randrange(0, len(available_directions))
        # we return it
        return available_directions[numb]
    # if no available directions, we get a random direction from the ones available to the room just to keep going
    else:
        dir = []
        directions = current_room.get_exits()
        for d in directions:
            dir.append(d)
        numb = random.randrange(0, len(dir))
        # we return the room
        return dir[numb]


# initiate the graph
graph = Graph()
# we keep track of the used directions for when we come back
used_directions = {}
# dict with directions and oppositions. Handy when we are setting directions in the graph for prev room and current room
options = {
    'n': 's',
    's': 'n',
    'e': 'w',
    'w': 'e'
}
# we create a Stack
s = Stack()
# the stack will keep track of a combination of direction that we come from, previous room, and the current player room. In this format: # [(direction, prev room), current_room]
# we push the first room. Since there is no precedent nor previous room, both will be None
s.push([[[None, None], player.current_room]])
# while the stack is not empty
while s.size() > 0:
    # we set a condition to exit the loop. Once we have traversed the whole maze, and we have as many room as there were in the original file, we stop. Othwerwise, we execute the code.
    if len(graph.vertices) != len(room_graph):
        # We pop the item on top of the Stack
        path = s.pop()
        # we extract the room. I know, it can be done with destructuring. This is a first pass
        room = path[-1][1]
        # we extract the direction where we are coming from
        incoming_direction = path[-1][0][0]
        # we extract the previous room
        prev_room = path[-1][0][1]
        # we get all available direction in the existing room
        directions = room.get_exits()
        # if we have not been in this room, there won't be any room in our graph. Therefore, we need to create it.
        if room.id not in graph.vertices:
            # we create the room
            graph.add_vertex(room.id)
            # and we set all available directions to "?" because we don't know yet where they all lead to. But we know they are available.
            for d in directions:
                graph.vertices[room.id][d] = "?"
        # if it is not the first time we run this code (we are not in starting room 0) we need to replace "?" with the directions that we are moving from and into. We compare this to None to knoe whether it is the first time we run this code (we are in room 0). If it is, incoming direction will be None.
        if incoming_direction != None:
            # we find the opposite direction we took
            opposite_direction = options[incoming_direction]
            # we set opposite direction in our room (i.e. if we took 'n' in the previous room, we need to set 's' in current room)
            graph.vertices[room.id][opposite_direction] = prev_room.id
            # we set the direction we took in the previous room (i.e. if we took 'n' we set 'n' to the id of the current room)
            graph.vertices[prev_room.id][incoming_direction] = room.id
        # the aim of the challenge is to traverse all the maze. For that, we need to find the directions in the current room that are marked as "?". We also want to keep track of the one we have taken in order to back up when we are tracing back our steps (i.e. when we reach dead end, we need to go back)
        # the following code takes care of knowing which directions are still unexplored and which ones have been taken.
        # directions with "?" on it
        unexplored_dir = []
        # direction that have not a "?" on it
        explored_dir = []
        # we iterate over all directions that our room has available
        for d in graph.vertices[room.id]:
            # if the direction has a "?" on it, it is available.
            if graph.vertices[room.id][d] == "?":
                # Therefore, we add it to the list of unexplored directions
                unexplored_dir.append(d)
            # if we just entered the room for the first time, there won't be any room in 'used_directions' and all of them are "?". Also, if the direction we are looping through has not been used
            if room.id not in used_directions or d not in used_directions[room.id]:
                # we add the direction to the list of explored directions
                explored_dir.append(d)
        # if there are unexplored directions
        if len(unexplored_dir) > 0:
            # we get a random direction to explore
            next_dir = get_random_direction(unexplored_dir, room)
            # we add the direction to the list of directions used in 'used_directions'.
            # If the room in that dict doesn't exist yet, we create
            if room.id not in used_directions:
                used_directions[room.id] = set()
            # if the room exists, we add the direction
            used_directions[room.id].add(next_dir)
            # we move the player to the next direction
            player.travel(next_dir)
            # we add the path to the path
            traversal_path.append(next_dir)
            # we duplicate the current trace of rooms in the Stack
            new_path = list(path)
            # we add new information based on the current player and direction and room where we come from
            new_path.append([[next_dir, room], player.current_room])
            # we push it to the stack
            s.push(new_path)
        # if len(unexplored_dir) == 0, it means we have reached a dead end. We need to go back.
        else:
            # we get a random direction from the explored directions that are not the ones we have used
            next_dir = get_random_direction(explored_dir, room)
            # same logic as before
            if room.id not in used_directions:
                used_directions[room.id] = set()
            used_directions[room.id].add(next_dir)
            player.travel(next_dir)
            traversal_path.append(next_dir)
            new_path = list(path)
            new_path.append([[next_dir, room], player.current_room])
            s.push(new_path)
    else:
        # we empty the stack to exit the loop
        while s.size() > 0:
            s.pop()


# print(graph.vertices, "<<<< vertices <<<<")
# print(traversal_path, "<<< path <<<")

# TRAVERSAL TEST
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
