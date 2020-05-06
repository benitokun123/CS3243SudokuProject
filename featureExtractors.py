# featureExtractors.py
# --------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"Feature extractors for Pacman game states"

from game import Directions, Actions
import util


class FeatureExtractor:
    def getFeatures(self, state, action):
        """
          Returns a dict from features to counts
          Usually, the count will just be 1.0 for
          indicator functions.
        """
        util.raiseNotDefined()


class IdentityExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[(state, action)] = 1.0
        return feats


class CoordinateExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[state] = 1.0
        feats['x=%d' % state[0]] = 1.0
        feats['y=%d' % state[0]] = 1.0
        feats['action=%s' % action] = 1.0
        return feats

def toInt(pos):
    x, y = pos
    x, y = int(x), int(y)
    return x, y

def closestFood(pos, food, walls):
    """
    closestFood -- this is similar to the function that we have
    worked on in the search project; here its all in one place
    """
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find a food at this location then exit
        if food[pos_x][pos_y]:
            return dist
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))
    # no food found
    return None

def closestGhost(pos, ghosts, walls, ghostStates):
    """
    return distance of closest scared ghost if it exists
    """

    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if dist > 2:
            return None
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find a food at this location then exit
        for g, s in zip(ghosts, ghostStates):
            ghostPos = toInt(g)
            if ghostPos == (pos_x, pos_y) and s.scaredTimer == 0:
                return dist
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))
    return None

def closestScaredGhost(pos, ghostStates, walls):
    """
    return distance of closest scared ghost if it exists
    """
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        for s in ghostStates:
            ghostPos = toInt(s.getPosition())
            if s.scaredTimer and ghostPos == (pos_x, pos_y):
                return dist
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))
    return None


def closestManhattanScaredGhost(pos, ghostStates):
    """
    return manhattan distance of closest scared ghost
    """
    dist = 1e9
    for s in ghostStates:
        if s.scaredTimer > 0:
            dist = min(dist, util.manhattanDistance(s.getPosition(), pos))
    
    if dist < 1e9:
        return dist
    return None

def closestCapsule(pos, capsules, walls):
    """
    return distance to closest capsule if it exists
    """
    
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find a food at this location then exit
        for c in capsules:
            if c == (pos_x, pos_y):
                return dist
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))
    return None

def findMaxTimeScared(ghostStates):
    maxTime = 0
    for s in ghostStates:
        if s.scaredTimer > maxTime:
            maxTime = s.scaredTimer
    return maxTime


class SimpleExtractor(FeatureExtractor):
    """
    Returns simple features for a basic reflex Pacman:
    - whether food will be eaten
    - how far away the next food is
    - whether a ghost collision is imminent
    - whether a ghost is one step away
    """

    def getFeatures(self, state, action):
        # extract the grid of food and wall locations and get the ghost locations
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostPositions()

        features = util.Counter()

        features["bias"] = 1.0

        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        # count the number of ghosts 1-step away
        features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)

        # if there is no danger of ghosts then add the food feature
        if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
            features["eats-food"] = 1.0

        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist) / (walls.width * walls.height)
        features.divideAll(10.0)
        return features


class NewExtractor(FeatureExtractor):
    """
    Design you own feature extractor here. You may define other helper functions you find necessary.
    """

    def getFeatures(self, state, action):
    	"""
        - whether food will be eaten
    		- how far away the next food is
    		- whether a ghost collision is imminent
    		- whether a ghost is one step away
        
        Things to implement additionally:
        - Pacman goes towards Capsule when Ghost is 5 grids away
        	--> Capsule must be near for this condition to take place
        - Pacman to go after ghosts when Ghosts are scared
        """

        """
        - PowerUp Mode
          -->	Distance from Ghost (go towards ghost if they are close)
          --> Power Up distance (Should be lowered so that it can be used next time)
          --> 
        - Non-PowerUp Mode
          -->	Distance from Ghost (get away from ghost)
          --> Power Up distance (if near should be higher)
          -->
        - BOTH
        	--> Closest Food
          --> Eat Food
        """

        "*** YOUR CODE HERE ***"
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostPositions()
        ghostStates = state.getGhostStates()
        capsules = state.getCapsules()

      	# Actions vectors
        # compute the location of pacman after he takes the action
      	x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)
        nextPos = (next_x, next_y)

        features = util.Counter()

        features["bias"] = 1.0

        hasScared = False
        for s in ghostStates:
          if s.scaredTimer > 0:
            hasScared = True
        
        if capsules:
            distCapsule = closestCapsule(nextPos, capsules, walls)
            if distCapsule is not None:
                features["closest-capsule"] = float(distCapsule) / (walls.width * walls.height)
            
        else:
            dist = closestFood((next_x, next_y), food, walls)
            if dist is not None:
              # make the distance a number less than one otherwise the update
              # will diverge wildly
              features["closest-food"] = float(dist) / (walls.width * walls.height)
              if food[next_x][next_y]:
                features["eats-food"] = 1.0

        if hasScared:
            distScaredGhost = closestScaredGhost(nextPos, ghostStates, walls)
            if distScaredGhost is not None:
                features["closest-scared-ghost"] = float(distScaredGhost) / (walls.width * walls.height)
            for g, s in zip(ghosts, ghostStates):
                if nextPos == g and s.scaredTimer > 0:
                    features["eat-scared-ghost"] = 1.0
            features["closest-capsule"] = 0

        features["#-of-ghosts-1-step-away"] = 0
        for g, s in zip(ghosts, ghostStates):
            if s.scaredTimer == 0:
                features["#-of-ghosts-1-step-away"] += nextPos in Actions.getLegalNeighbors(g, walls)
        for g, s in zip(ghosts, ghostStates):
            if nextPos == g and s.scaredTimer == 0:
                features["die-to-ghost"] = 1.0

        features.divideAll(10.0)
        return features
