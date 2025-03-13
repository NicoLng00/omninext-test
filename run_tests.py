import unittest
from Tests.Users.TestGetUser import TestGetUser
from Tests.Users.TestCreateUser import TestCreateUser

if __name__ == '__main__':
    # Crea una suite di test
    test_suite = unittest.TestSuite()
    
    # Aggiungi le classi di test
    test_suite.addTest(unittest.makeSuite(TestGetUser))
    test_suite.addTest(unittest.makeSuite(TestCreateUser))
    
    # Esegui i test
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite) 