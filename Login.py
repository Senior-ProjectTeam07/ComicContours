from tkinter import *



#create main window
window = Tk()
window.title('Facial Feature Augmentation using GAN')
window.geometry("400x150")

#make a label for the window
Label(window,text="Facial Feature Augmentation").grid(row=0) 
 
Label(window,text="Email").grid(row=1)
Label(window,text="Password").grid(row=2) 
Label(window,text="Forgot Password?",font=('Times New Roman', 8)).grid(row=3) 
Entry(window).grid(row=1, column=1)
Entry(window).grid(row=2, column=1)

button = Button(window, text='Login', width=25, command=window.destroy) 
button.grid(row=4,column=1)
button = Button(window, text='Create Account', width=15, command=window.destroy) 
button.grid(row=5,column=0)
#run forever
window.mainloop()