# test the FileServer
# before calling "python FileServerTest.py", make sure this is set:
# export PYTHONPATH="/opt/Ice-3.4.2/python:test/UnitTests/python"
import sys, traceback
#sys.path.append('''c:\Program Files (x86)\Zeroc\Ice-3.4.2\python''')
#sys.path.append('''C:\Users\tomb\Documents\nps\git\myCVAC\CVACvisualStudio\test\UnitTests\python''')
#sys.path.append('''C:\Users\tomb\Documents\nps\git\myCVAC\CVACvisualStudio\test\UnitTests\python\cvac''')
sys.path.append('''.''')
import Ice
if "C:\Program Files (x86)\ZeroC_Ice\python" not in sys.path:
    sys.path.append("C:\Program Files (x86)\ZeroC_Ice\python")
import Ice
import IcePy
import cvac
import unittest
import os
import inspect
import tempfile
import filecmp
import shutil

class FileServerTest(unittest.TestCase):

    ic = None
    fs = None
    dataDir = None
    
    #
    # Test the initialization of Ice and the service proxy
    #
    def setUp(self):
        if not 'FileServicePrx' in dir( cvac ):
            # import os
            # print os.environ['PYTHONPATH'].split(os.pathsep)
            raise RuntimeError("cvac module not loaded correctly (from file "+cvac.__file__+")")
        if not inspect.ismodule( cvac ) or not inspect.isclass( cvac.FileServicePrx ):
            raise RuntimeError("cvac module not loaded")
        self.ic = Ice.initialize(sys.argv)
        base = self.ic.stringToProxy("FileServer:default -p 10013")
        self.fs = cvac.FileServicePrx.checkedCast(base)
        if not self.fs:
            raise RuntimeError("Invalid proxy")

        # Since this is a test, it's probably run in the build directory. We
        # need to know the path to the original files for various operations, but we
        # don't have easy access to the CVAC.DataDir variable.  Let's guess.
        self.dataDir = "../../../../data"
        if not os.path.exists( self.dataDir ):
            print "Present working directory: " + os.getcwd()
            print "Looking for CVAC.DataDir at: " + self.dataDir
            raise RuntimeError("Cannot obtain path to CVAC.DataDir, see comments")


    #
    # Test if we can get a file, copy bytes to a tempfile, compare
    #
    def test_getFile(self):
        print 'getFile'
        # test with a small file for now
        testDir = cvac.DirectoryPath( "testImg" );
        filePath = cvac.FilePath( testDir, "TestUsFlag.jpg" )
        self.getFileAndCompare( filePath )

    #
    # Test if we can put a file, compare results;
    # Test that we can delete this file on the server again;
    # Test that overwriting an existing file fails;
    #
    def test_putFile(self):
        # create a copy of the existing TestKrFlag.jpg in a tempfile
        testDir = cvac.DirectoryPath( "testImg" );
        filePath = cvac.FilePath( testDir, "TestKrFlag.jpg" )
        orig = self.dataDir+"/"+filePath.directory.relativePath+"/"+filePath.filename
        if not os.path.exists( orig ):
            print "Present working directory: " + os.getcwd()
            print "Looking for file: " + orig
            raise RuntimeError("Cannot obtain path to original file, see comments")
        ftmp = tempfile.NamedTemporaryFile( suffix='.jpg', delete=True, dir=self.dataDir )
        shutil.copy( orig, ftmp.name )
        
        # "put" the tempfile and compare the result via file system access
        self.fs.putFile( filePath, bytes );

        # delete the "put" file on the server

        # try to "put" an existing file; this should fail

        # close the tempfile
        return

    def getFileAndCompare( self, filePath ):
        bytes = self.fs.getFile( filePath )
        if not bytes:
            raise RuntimeError("could not obtain file from '"
                               +filePath.directory.relativePath+"/"+filePath.filename+"'")

        # Write bytes to a temp file and compare the contents to the orig.
        # Since this is a test, it's probably run in the build directory. We
        # need to know the path to the original file for the compare, but we
        # don't have easy access to the CVAC.DataDir variable.  Let's try to
        # figure it out from the 'pwd'
        orig = self.dataDir+"/"+filePath.directory.relativePath+"/"+filePath.filename
        if not os.path.exists( orig ):
            print "Present working directory: " + os.getcwd()
            print "Looking for file: " + orig
            raise RuntimeError("Cannot obtain path to original file, see comments")
        
        ftmp = tempfile.NamedTemporaryFile( suffix='.jpg', delete=True )
        ftmp.write( bytes )
        ftmp.flush()
        if not self.filesAreEqual( orig, ftmp.name ):
            print "comparison failed, new file: " + ftmp.name
            ftmp.close()
            raise RuntimeError("file was not copied correctly")
        ftmp.close()

    def filesAreEqual(self, fname1, fname2):
        # import difflib
        # print difflib.SequenceMatcher(None, orig, tfile.name)
        # forig = open( orig )
        # diff = difflib.ndiff(forig.readlines(), ftmp.readlines())
        # delta = ''.join(x[2:] for x in diff if x.startswith('- '))
        return filecmp.cmp( fname1, fname2 )

    def tearDown(self):
        # Clean up
        if self.ic:
            try:
                self.ic.destroy()
            except:
                traceback.print_exc()
                status = 1

if __name__ == '__main__':
    unittest.main()
