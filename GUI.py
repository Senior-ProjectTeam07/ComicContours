from tkinter import *



#create main window
window = Tk()
window.title('Facial Feature Augmentation using GAN')
window.geometry("700x150")

mb =  Menubutton ( window, text = 'Menu')
mb.menu = Menu(mb)   
mb["menu"]= mb.menu   
  
var1 = IntVar() 
var2 = IntVar() 
var3 = IntVar() 
var4 = IntVar() 

mb.menu.add_checkbutton(label = "Logout", 
                                variable = var1)   
mb.menu.add_checkbutton(label = "About", 
                                variable = var2) 
mb.menu.add_checkbutton(label = "Terms of Use", 
                                variable = var3) 
mb.menu.add_checkbutton(label = "Database", 
                                variable = var4)
mb.grid(row=0,column=5)
#make a label for the window
Label(window,text="Welcome to Facial Feature Augmentation").grid(row=0) 
#make a button for the window
button = Button(window, text='Upload image', width=25, command=window.destroy) 
button.grid(row=1,column=0)
var1 = IntVar() 
Checkbutton(window, text='I consent to having the photo and caraciture added to a database for facial recognition reasearch pruposes only.', variable=var1).grid(row=2, sticky=W)  
#run forever
window.mainloop()