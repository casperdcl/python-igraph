from __future__ import with_statement

import unittest
from igraph import *
import tempfile
import os

from contextlib import contextmanager
from textwrap import dedent

@contextmanager
def temporary_file(content):
    tmpf, tmpfname = tempfile.mkstemp()
    os.close(tmpf)
    tmpf = open(tmpfname, "w")
    print >>tmpf, dedent(content)
    tmpf.close()
    yield tmpfname
    os.unlink(tmpfname)


class ForeignTests(unittest.TestCase):
    def testDIMACS(self):
        with temporary_file("""\
        c
        c        This is a simple example file to demonstrate the
        c     DIMACS input file format for minimum-cost flow problems.
        c 
        c problem line :
        p max 4 5
        c
        c node descriptor lines :
        n 1 s
        n 4 t
        c
        c arc descriptor lines :
        a 1 2 4
        a 1 3 2
        a 2 3 2
        a 2 4 3
        a 3 4 5
        """) as tmpfname:
            g, src, dst, cap=Graph.Read_DIMACS(tmpfname, False)
            self.failUnless(isinstance(g, Graph))
            self.failUnless(g.vcount() == 4 and g.ecount() == 5)
            self.failUnless(src == 0 and dst == 3)
            self.failUnless(cap == [4,2,2,3,5])
            g.write_dimacs(tmpfname, src, dst, cap)


    def testDL(self):
        with temporary_file("""\
        dl n=5
        format = fullmatrix
        labels embedded
        data:
        larry david lin pat russ
        Larry 0 1 1 1 0
        david 1 0 0 0 1
        Lin 1 0 0 1 0
        Pat 1 0 1 0 1
        russ 0 1 0 1 0""") as tmpfname:
            g = Graph.Read_DL(tmpfname)
            self.failUnless(isinstance(g, Graph))
            self.failUnless(g.vcount() == 5 and g.ecount() == 12)
            self.failUnless(g.is_directed())
            self.failUnless(sorted(g.get_edgelist()) == \
                    [(0,1),(0,2),(0,3),(1,0),(1,4),(2,0),(2,3),(3,0),\
                     (3,2),(3,4),(4,1),(4,3)])

        with temporary_file("""\
        dl n=5
        format = fullmatrix
        labels:
        barry,david
        lin,pat
        russ
        data:
        0 1 1 1 0
        1 0 0 0 1
        1 0 0 1 0
        1 0 1 0 1
        0 1 0 1 0""") as tmpfname:
            g = Graph.Read_DL(tmpfname)
            self.failUnless(isinstance(g, Graph))
            self.failUnless(g.vcount() == 5 and g.ecount() == 12)
            self.failUnless(g.is_directed())
            self.failUnless(sorted(g.get_edgelist()) == \
                    [(0,1),(0,2),(0,3),(1,0),(1,4),(2,0),(2,3),(3,0),\
                     (3,2),(3,4),(4,1),(4,3)])
        
        with temporary_file("""\
        DL n=5
        format = edgelist1
        labels:
        george, sally, jim, billy, jane
        labels embedded:
        data:
        george sally 2
        george jim 3
        sally jim 4
        billy george 5
        jane jim 6""") as tmpfname:
            g = Graph.Read_DL(tmpfname, False)
            self.failUnless(isinstance(g, Graph))
            self.failUnless(g.vcount() == 5 and g.ecount() == 5)
            self.failUnless(not g.is_directed())
            self.failUnless(sorted(g.get_edgelist()) == \
                    [(0,1),(0,2),(0,3),(1,2),(2,4)])

    def testAdjacency(self):
        with temporary_file("""\
        # Test comment line
        0 1 1 0 0 0
        1 0 1 0 0 0
        1 1 0 0 0 0
        0 0 0 0 2 2
        0 0 0 2 0 2
        0 0 0 2 2 0
        """) as tmpfname:
            g = Graph.Read_Adjacency(tmpfname)
            self.failUnless(isinstance(g, Graph))
            self.failUnless(g.vcount() == 6 and g.ecount() == 18 and
                g.is_directed() and "weight" not in g.edge_attributes())
            g = Graph.Read_Adjacency(tmpfname, attribute="weight")
            self.failUnless(isinstance(g, Graph))
            self.failUnless(g.vcount() == 6 and g.ecount() == 12 and
                g.is_directed() and g.es["weight"] == [1,1,1,1,1,1,2,2,2,2,2,2])

            g.write_adjacency(tmpfname)


def suite():
    foreign_suite = unittest.makeSuite(ForeignTests)
    return unittest.TestSuite([foreign_suite])

def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())
    
if __name__ == "__main__":
    test()

