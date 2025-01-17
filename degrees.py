import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}

def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass

def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")

def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    frontier = QueueFrontier()
    explored_nodes = []
    explored_actors = []
    # expand Node
    neighbors = neighbors_for_person(source)
    # iterate over neighbors
    for neighbor in neighbors:
        # check if neighbor is equal to target
        if neighbor[1]  == target:
            # if equal, return tuple with movie_id and actor_id
            print(f"R1: Target found {people[neighbor[1]]['name']}")
            return [(neighbor[0],neighbor[1])]

        # if not equal: create Node and add to frontier
        elif (neighbor[1] != source and neighbor[1] not in explored_actors):
            frontier.add(Node(state=neighbor[1], parent=None, action=neighbor[0]))
            explored_actors.append(neighbor[1])

    target_missing = True
    explored_elements = []

    while target_missing:
        # remove Node from frontier (checking for empty status is implemented in remove())
        node = frontier.remove()
        if node == None:
            return None
        else:
            explored_nodes.append(node)
            explored_actors.extend([node.state])
            # expand Node
            neighbors = neighbors_for_person(node.state)
            # iterate over neighbors
            for neighbor in neighbors:
                # first check if neighbor is equal to target
                if neighbor[1] == target:
                    explored_nodes.append(Node(state=neighbor[1], parent=(node.action, node.state), action=neighbor[0]))
                    target_missing = False
                    return get_answer(explored_nodes)
                # if not equal, create Node and add to frontier
                elif (neighbor[1] != source and neighbor[1] not in explored_actors):
                    frontier.add(Node(state=neighbor[1], parent=(node.action, node.state), action=neighbor[0]))
                    explored_actors.append(neighbor[1])

def get_answer(explored_nodes):
    answer = []
    last_node = explored_nodes.pop()
    answer.append((last_node.action, last_node.state))
    while last_node.parent != None:
        last_node = get_node(explored_nodes, last_node.parent)
        #if last_node.parent != None:
        answer.insert(0,(last_node.action, last_node.state))
    return answer

def get_node(explored_nodes, parent):
    for node in explored_nodes:
        if (node.state == parent[1] and node.action == parent[0]):
            return node

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]

def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors

if __name__ == "__main__":
    main()
