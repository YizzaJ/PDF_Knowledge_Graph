from bs4 import BeautifulSoup
import Script.preprocess as p

'''
Tests for the preprocessing.py script.
---------------------------------------------

For this we will use sample files
inside the samples folder. This are:
-test1.xml: has only a title.
-test2.xml: has only an abstract.
-test3.xml: has only an acknowledgment.
-test4.txt: has some project number samples.
'''



def get_xml(file):
    with open("./samples/" + file, 'r', encoding="utf-8") as tei:
        return BeautifulSoup(tei, 'xml')
    
def get_txt(file):
    with open("./samples/" + file, 'r', encoding="utf-8") as txt:
        return txt.read()

# Test that should find the title in the xml.
def test_get_title(): 
    soup = get_xml("test1.xml")
    assert p.get_title(soup) == ("TITLE1")

# Test that should find no title in the xml.
def test_get_no_title(): 
    soup = get_xml("test2.xml")
    assert p.get_title(soup) == ("")

# Test that should find the abstract in the xml.
def test_get_abstract(): 
    soup = get_xml("test2.xml")
    assert p.get_abstract(soup) == ("ABSTRACT")

# Test that should find no abstract in the xml.
def test_get_no_abstract(): 
    soup = get_xml("test1.xml")
    assert p.get_abstract(soup) == ("")

# Test that should find the acknowledgement in the xml.
def test_get_acknowledgements(): 
    soup = get_xml("test3.xml")
    assert p.get_acknowledgements(soup) == ("ACKNOWLEDGEMENTS")

# Test that should find the acknowledgement in the xml.
def test_get_no_acknowledgements(): 
    soup = get_xml("test2.xml")
    assert p.get_acknowledgements(soup) == ("")

# Test that should find a list of projects given some text.
def test_get_projects(): 
    ack = get_txt("test4.txt")
    assert p.extract_projects(ack) == (['2004.03.0122.001', 'M01RR00188', 'Z01-DC-00060', '71301059', 'B200202028', 'N00014-13-1-0720'])

# Test that should find no projects given some text.
def test_get_no_projects(): 
    ack = get_txt("test2.xml")
    assert p.extract_projects(ack) == ([])
