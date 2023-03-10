menu = """
    \n\n                                                            
      _______   __     __       ____        _______    __________   
     / ______| |  \\  /  |      /    \\      / _____|   /  /   /  /|
     |  \___   |   \\/   |     /  /\  \\     | \___    /_ /___/ _/ | 
      \____ \\  |        |    /  /__\\  \\     \____ \\  |         | |
      _____| | | |\\  /| |   /  ______  \\   _____| |  |         | |
     |______/  |_| \\/ |_|  /__/      \\__\\  |______/  |_________|/
                                        
                                        - By Xin Li
                                              
        """
print(menu)

Ld=MethodLoader(builtFilePath, direct, file)
                    self.attackMethod_dict = Ld.set_attackMethod_dict()
                    for md in self.attackMethod:
                        self.methodname = md
                        if self.methodname in self.attackMethod_dict.keys():
                            Ld.add_attackMethodName(self.methodname)
                            task = Ld.run()
                            task()
                        else:
                            pass
