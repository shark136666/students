import traitlets
from ipywidgets import widgets
from IPython.display import display
from tkinter import Tk, filedialog


class SaveFilesButton(widgets.Button):
    """A file widget that leverages tkinter.filedialog."""

    def __init__(self, file_data):
        super(SaveFilesButton, self).__init__()
        # Add the selected_files trait
        #self.add_traits(files=traitlets.traitlets.List())
        # Create the button.
        self.description = "SaveFiles"
        self.icon = "square-o"
        self.style.button_color = "orange"
        # Set on click behavior.
        self.on_click(self.select_files)
        self.file_data = file_data

    @staticmethod
    def select_files(b):
        """Generate instance of tkinter.filedialog.

        Parameters
        ----------
        b : obj:
            An instance of ipywidgets.widgets.Button 
        """
        # Create Tk root
        root = Tk()
        # Hide the main window
        root.withdraw()
        # Raise the root to the top of all windows.
        root.call('wm', 'attributes', '.', '-topmost', True)
        # List of selected fileswill be set to b.value
        files = [('HTML', '*.html')]
        b.files = filedialog.asksaveasfilename(defaultextension=".html",filetypes=files)
        f = open(b.files, 'w')
        s = b.file_data
        f.write(s)
        f.close()        

        b.description = "Files Saved"
        b.icon = "check-square-o"
        b.style.button_color = "lightgreen"