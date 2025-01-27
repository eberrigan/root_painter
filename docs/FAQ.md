### Frequently asked questions (at least once)

#### Question - [Skipping to images](https://github.com/Abe404/root_painter/issues/59)
I wanted to skip back to the first few images I've used to show the annotation approach/progress. Is there any easier way to do it than pressing back and waiting for each image to load?

#### Answer:
With the project open, go to the extras menu and view metrics plot. Then click on the image point in the metrics plot and it will take you to the corresponding image in the viewer.


#### Question - Why is the segmentation not loading?

#### Answer:

My best guess is that there is a delay in sync or the sync software is not set up and/or working properly. There might be another problem (such as a bug with RootPainter) but here are a few steps to help you isolate the problem:

1. **Check the sync directory is speciﬁed correctly**. In your home directory i.e the user directory, there is a ﬁle called root_painter_settings.json. You can open this ﬁle in a text editor to see which directory is speciﬁed as the sync directory. You can also just manually set a new sync directory (to make sure it is correct) using the option from the extras menu. The sync directory should be set as a path to the drive_rp_sync folder if inside your google drive on your local computer, if you are following the colab tutorial. Otherwise it should be the folder setup to share data between the RootPainter client and server (which was also specified when you started the RootPainter server).

2. **Check segmentation instructions are being created**. 
Without starting the trainer (server) , open the client (GUI) and go to an image that doesn’t already have a segmentation. You should see ‘loading segmentation’ in the client. At this point the client should also create an instruction (just a text ﬁle) in the instructions folder which is inside the sync folder. If you are following the colab tutorial then your sync folder is a folder in your google drive called drive_rp_sync. This instruction ﬁle is a text ﬁle that tells the server which image to segment. You can conﬁrm this ﬁle is being created correctly by checking the instruction folder on your computer and checking if the instruction ﬁle exists. You need to do this step without the server running, because if the server is running it will delete the instruction as soon as it has read it. I suggest checking your local google drive folder ﬁrst. This should exist on your local machine. If the instructions are never being created in the correct location then there may be a problem with the sync directory or perhaps some permissions issues.


3. (if you are using colab) **Check segmentation instruction is being synced to google drive**. The colab tutorial assumes you have set up and installed google drive for desktop. If you have google drive for desktop up and running and then the sync folder speciﬁed correctly then instructions should get created in your local instructions folder. These instructions should also get synced to google drive. If you have ﬁrst conﬁrmed the instructions are created correctly then you can check your online google drive to see if they are synced with google's servers. Go to the following url: https://drive.google.com/drive/u/0/my-drive (or just navigate to your google drive online using a web browser) and then go to the drive_rp_sync folder (that was created as part of the colab tutorial). Inside you should see an instructions folder and in the instructions folder should be the instruction ﬁle that was created locally on your computer using the RootPainter client (the GUI application). If you do see the instruction ﬁle locally but you don’t see it online then it indicates there is a problem with synchronization of ﬁles from your computer to google drive.

4. (if you are using colab). **Inspect the status of google drive for desktop** (that should be running on your computer). It could be delayed, busy syncing many ﬁles or not set up to sync the correct locations. In some rare cases it can be buggy and you may want to try uninstalling it and reinstalling again to get sync working properly.

5. **Check for errors in the server output**. When
running both client and server together, inspect the console output for the server in colab. You should see output after you start the server (which should be left running whilst using RootPainter). For example, if you view an image in the client named CHNCXR_0068_0.jpg that does not have a segmentation yet, it then you should see the following output from the server console:


  > execute_instruction segment
  
  > ensemble segment CHNCXR_0068_0.jpg, dur 0.2
  
  > Seconds to segment 1 images:  0.237

Note: Sometimes due to slow sync time it will appear after a delay, so wait a couple of minutes just to be sure there isn’t some delay in sync.


6. **Inspect the console output for the client**. The most recent versions of RootPainter (https://github.com/Abe404/root_painter/releases/) should open a black console that displays error messages from time to time. Perhaps something is going wrong and the output will give us a clue.


Hopefully, even if it doesn’t solve the problem, these instructions will help you get more information that will help us figure out what is going wrong. If you think you have found a bug in the software then feel free to report an issue (https://github.com/Abe404/root_painter/issues) 

