# CS1210 Homework3
#
# This file should contain only your own work; there are no partners
# assigned or permitted for Homework assignments.
#
# I certify that the entirety of this file contains only my own work.
# I have not shared the contents of this file with anyone in any form,
# nor have I obtained or included code from any other source aside
# from the code contained in the original homework template file.
import re
from string import punctuation
import matplotlib.pyplot as plt
import networkx as nx

######################################################################
# Edit the following function definition so it returns a tuple
# containing a single string, your hawkid.
######################################################################
def hawkid():
    return(("kvarnr",))

######################################################################
# Regular expressions to expand contractions. Ordering reflects
# application order.
RE = ( ("([a-z])n['’]t\\b","\\1 not"),        # (provided)
       ("([a-z])['’]d\\b", "\\1 had"), 
       ("([a-z])['’]ve\\b", "\\1 have"), 
       ("([a-z])['’]s\\b", "\\1 is"),         # Messes up possessives (['’]s).
       ("([a-z])['’]m\\b", "\\1 am"),
       ("([a-z])['’]re\\b", "\\1 are"), 
       ("([a-z])['’]ll\\b", "\\1 will"),
       ("\\bma['’]a?m\\b", "madam"),	   # (provided) Abbrevs like Mme.?
       ("\W([a-z])-([a-z])", "\\1\\2"),    # (provided) Merge stutters
       ("-+", " ") )			   # (provided) Split words at hyphens.

######################################################################
# readFile(filename, regexes) returns a list of words read from the
# specified file. The second argument is a list of regular expressions
# that should be applied to the text before stripping punctuation from
# the words in the text.
def readFile(F, regexes = RE):
    '''readFile(F, regexes = RE)
           Reads book from file F and returns it in the form of a list 
           of "cleaned up" (via application of regexes) single words.'''
    # Precompile substitution regexes.
    regexes = [ (re.compile(regex[0], re.IGNORECASE), regex[1]) for regex in regexes ]
 
    # Open file for reading.
    L = []
    file = open(F, 'r')
    for line in file:
        # Ditch empty lines or lines that are all caps
        if line.strip() != '' and line.upper() != line:
            # Apply regex corrections to the resulting string
            # and collect surviving lines.
            for regex in regexes:
                line = regex[0].sub(regex[1], line)
            L.append(line)
    file.close()

    # Produce a word list.
    W = ' '.join(L).split()
    print("Read {} words".format(len(W)))

    # Return the list of words, stripping punctuation as you go.
    return([ w.strip(punctuation) for w in W if len(w.strip(punctuation)) > 0 ])

######################################################################
# findNouns(W, cmin=1) returns a dictionary of proper nouns (as keys)
# and their occurrance counts (as values) provided each key noun
# appears at least cmin times in the text.
def findNouns(W, cmin=1):
    '''findNouns(W, cmin=1)
           Identifies a set of proper nouns from word list W. Proper nouns
           are words that only appear in capitalized form. Returns a dictionary
           of proper nouns occurring at least cmin times with their respective
           occurrance count as the value.'''
    # Count noun candidates
    N = {}
    # Scan words in book for nouns (or noun clusters?)
    for w in W:
        # A noun appears titlecase; moreover, aside from 'I' is longer
        # than 1 letter.
        if w.capitalize() == w and (len(w)>1 or w == 'I'):
            # A noun candidate
            if w.lower() not in N:
                N[w.lower()] = 1
            elif N[w.lower()] > 0:
                N[w.lower()] = N[w.lower()] + 1
    print("Found {} candidate nouns".format(len(N)))

    # Now discard nouns that appeared elsewhere in lowercase or didn't
    # appear often enough to matter.
    for w in W:
        if (w.lower() in N and (w == w.lower() or N[w.lower()] < cmin)):
            del N[w.lower()]
    print("Retaining {} common nouns".format(len(N)))
    return(N)

######################################################################
# buildIndex(W, N) returns a dictionary of proper nouns (as keys)
# taken from N and the index value in W for each occurrance of the key
# noun.
def buildIndex(W, N):
    '''buildIndex(W, N)
           Takes as input a word list W and a proper noun dictionary
           N with noun:count entries and returns a dictionary with
           noun:list-of-indeces entries, where each index is a list of 
           locations in W.'''
    # Initialize the index.
    I = { noun:[] for noun in N }

    # Construct an index.
    for i in range(len(W)):
        if W[i].lower() in I:
            I[W[i].lower()].append(i)
    return(I)

######################################################################
# plotChars(N, I, W, xsteps=10) uses matplotlib to plot a character
# plot like the one shown in the handout, where N is a dictionary of
# proper nouns (as returned by findNouns()), I is an index of proper
# nouns and their locations in the text (as returned by buildIndex()),
# W is a list of words in the text (as returned by readFile()) and
# xsteps is the window size within which we count occurrences of each
# character.
def plotChars(N, I, W, xsteps=10):
    '''plotChars(N, I, W, xsteps=10)
           Takes as input an index of proper nouns N (format noun:occurrances),
           a similar index I (format noun:list-of-indeces), and
           a word list W, producing a plot of character activity as
           a function of location in the book represented by W.
           Optional argument xsteps governs the granularity of the plot.'''
    # Plot characters in C according to their index.
    # Helper function.
    def occur(c, I, lo, hi):
        return( len([ loc for loc in I[c] if loc >= lo and loc < hi ]) )

    # Can step over keys of either I or N, although if I use N, I can
    # recompute N and reuse previously computed I (provided new N has
    # fewer nouns than the N used to buildIndex()).
    C = { c:([0] + [ occur(c, I, i*len(W)//xsteps, (i+1)*len(W)//xsteps) for i in range(0, xsteps) ]) for c in N.keys() }
    ymax = round(1.3*max([ max(v) for v in C.values() ]))

    # Plot title and axis labels.
    plt.title('Character plot')
    plt.axis( [ 0, xsteps, 0, ymax ] )
    plt.xlabel('Location (text%)')
    plt.ylabel('Mentions')
    if xsteps > 10:
        plt.xticks([ x for x in range(0, xsteps+1, xsteps//10) ], [ str(p) for p in range(0, 101, 10) ])
    else:
        plt.xticks(list(range(xsteps)), [ str(p) for p in range(0, 101, 100//xsteps) ])
    plt.yticks([ y for y in range(0, ymax, ymax//10) ])

    # Set up characters.
    for c in C.keys():
        plt.plot( [ x for x in range(xsteps+1) ], C[c], label=c.capitalize() )
    # Show labels.
    plt.legend(loc='upper left')
    # Display it.
    plt.show()

######################################################################
# mapChars(N, I. imin, imax, dmax) uses networkx and matplotlib to
# plot a graph linking characters (nodes) to each other with a set of
# weighted edges, where each edge represents the number of occurrences
# of the two characters within dmax words of each other for each
# character occurrance between words imin and imax in the text.
def mapChars(N, I, imin, imax, dmax):
    '''Function starts with an empty data set as a list and then analyzes the
        text in chunks, determined by xsteps, to see which characters are referenced
        together in that chunk of text and how often this occurs. From there a tuple
        is built that lists the names of character and character2 along with the third
        value being a dictionary of the 'weight' (the occurance of the reference) as
        the key and the total number of occurances as the value. from there it is plotted
        with the lenght of the line being the weight. The longer the lines the less often
        the occurance. The shorter the lines the more often they occur.'''
    dataset = [] #Creates an empty dataset as a list
    for character in N.keys(): #for each character in the keys of dictionary N
        for value in I[character]: #for value in dictionary I indexed at the character
            if value in range(imin, imax): #if the value is in the range of the max and min
                for character2 in I.keys(): #for the 2nd character in the dictionary I
                    if character == character2: #if character is the same as the 2nd character
                        continue #continue on with the function below
                    else: #if character doesn't equal the 2nd character then do
                        for value2 in I[character2]: #for each instance of character2 in I indexed at that character
                            if value2 in range(value-dmax, value+dmax+1): #if character 2 is in the range of value plus and minus the window max (dmax)
                                if {character, character2} in [data[0] for data in dataset]: #if the tuple of characters 1 and 2 are already in a data in the dataset
                                    for element in range(len(dataset)): #for every element in the the range of the lenght of the dataset
                                        if dataset[element][0] == {character, character2}: #if the dataset indexed at the first element of the dataset equals the dictionary of character and character2 then
                                            dataset[element][1]['weight'] += 1 #add 1 to the value in the dictionary in the dataset where 'weight' is the key
                                else:
                                    dataset.append(({character, character2}, {'weight': 1})) #if they are not equivilent then append the 2 characters to the list and set the weight to 1
                            elif value2 > dmax + value: #if the walue of the character is greater than the window max plus the value of the character where it was indexed
                                break #then break from the loop and continue with the function
            elif value > imax: #if the value from the characer index is greater than the max value of the chunk
                break #then break from the loop and continue on with the function
    dataset = [(tuple(data[0]), data[1]) for data in dataset] #establish the form of the function by establishing data points as the characters in the dataset list
    G = nx.Graph() #initializes the graph
    G.add_nodes_from([i for i in N.keys()]) #creates a point on the graph for each character in the tuple
    G.add_edges_from([(data[0][0], data[0][1], data[1]) for data in dataset]) #for each character in the dataset it draws the link between them
    nx.draw_spring(G, title = 'Relations Between Characters', with_labels=True) #formats the graph and gives it lables and a title
    plt.show() #makes the graph visible
            
######################################################################
# plot(file='wind.txt', cmin=100, xsteps=10) is a driver that manages
# the entire analysis and plotting process. It is presented to give
# you an idea of how to use the functions you've just designed.
def plot(file='wind.txt', cmin=100, xsteps=10):
    '''plot(file='wind.txt', cmin=100, xsteps=10)
           Convenient driver function to test system as a whole.'''
    W=readFile(file)
    N=findNouns(W, cmin)
    I=buildIndex(W, N)
    plotChars(N, I, W, xsteps)
    imax=len(W)//xsteps #sets the max to the lenght of the text divided by the number of steps chosen (also known as the chunk max)
    imin=0 #sets the minimum value to 0
    dmax = 100 #sets the max of the window to 100
    for i in range(xsteps): #for every element in the range of the chunk(xsteps)
        mapChars(N, I, imin, imax, dmax) #Initiates mapChars
        imax += len(W)// xsteps #increments imax by the chunk size
        imin += len(W) // xsteps #increments imin by the chunk size
