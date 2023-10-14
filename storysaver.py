# ===
# Script to save an story / article in a single html file.
# ===

# Imports.
import os
import dominate
import markdown
import PySimpleGUI as sg
import readtime
# ---

# Froms.
from pathvalidate import sanitize_filename
from dominate.util import raw
from dominate.tags import *
# ---

# Structures.
class Story:

    # Constructor
    def __init__(self):
        self.title = ""
        self.description = ""
        self.author = ""
        self.publisher = ""
        self.category = ""
        self.story_link = ""
        self.author_profile_link = ""
        self.category_link = ""
        self.story = ""
        self.markdown = False
        self.story_html = ""
    # ---

    # Converts Markdown to HTML.
    # Splits lines and converts paragraphs to <p/>
    def editorize(self):
        """Edit the values to make processing easier"""

        if self.markdown == True:
            self.story_html = markdown.markdown(self.story)
        else:
            contents = self.story.split("\n\n")
            for line in contents:
                self.story_html += str(p(line)) + "\n"
    # ---

    # Validates links and removes whitespace from start and end of strings.
    def validate(self):
        """Validate values to ensure correct processing"""

        if os.path.exists("exported") == False:
            os.mkdir("exported")

        if self.story_link == "":
            self.story_link = "#"

        if self.author_profile_link == "":
            self.author_profile_link = "#"

        if self.category_link == "":
            self.category_link = "#"

        if self.category == "":
            self.category = "General"\

        self.title = self.title.strip()
        self.description = self.description.strip()
        self.author = self.author.strip()
        self.publisher = self.publisher.strip()
        self.category = self.category.strip()
        self.story_link = self.story_link.strip()
        self.author_profile_link = self.author_profile_link.strip()
        self.category_link = self.category_link.strip()
        self.story = self.story.strip()
        self.markdown = False
        self.story_html = self.story_html.strip()

        # If any mandatory field is missing, do not allow saving the file.
        if self.title == "" or self.author == "" or self.publisher == "" or self.story == "":
            return False
        else:
            return True
    # ---

    # Saves the file in HTML. Adds a stylesheet and script to allow user to switch
    # themes between light and dark modes.
    def save(self):
        """Save the file in html"""

        self.editorize()

        # If validation is false, file should not be saved.
        if self.validate() == False:
            return None

        # Sanitized filename ensures there are no unacceptable characters in the filename string.
        file_name = sanitize_filename("[%s] %s - %s.html" %(self.publisher, self.author, self.title))

        # Fetch the required stylesheet.
        d_css_file = "styles.css"
        d_css = ""
        with open(d_css_file, "r") as f:
            d_css = f.read()

        # Object that holds the HTML file data.
        d = dominate.document(title=file_name)
        
        # Write the stylesheet in the <head/> of the HTML file.
        with d.head:
            style(raw(d_css), pretty=True)

        # Create the <div/> that contains the toggle button for light/dark mode.
        div_toggle = div(_class="toggle-button")
        div_toggle.add(input_(type="checkbox", _class="checkbox", id="chk"))
        label_toggle = label(_for="chk", _class="label")
        label_toggle.add(div(_class="ball"))
        div_toggle.add(label_toggle)

        # Add the toggle button <div/> created above to the HTML file.
        d += div_toggle

        # Add the title of the story and its link as <h3/> at the top of the page.
        div_title = div(_class="title")
        if self.story_link == "#":
        # "#" means that the link points to itself, so it's not necessary to
        # have it open in a new tab / window when clicked.
            div_title.add(h1(a(self.title, href=self.story_link)))
        else:
            div_title.add(h1(a(self.title, href=self.story_link, target="_blank")))

        d += div_title

        # Add the description to the HTML file.
        div_description = div(_class="description")
        div_description.add(h4(self.description))
        d += div_description

        # Create the <div/> that will contain the author, category, and read time.
        div_details = div(_class="details")

        if self.author_profile_link == "#":
        # "#" means that the link points to itself, so it's not necessary to
        # have it open in a new tab / window when clicked.
            div_author = a(href=self.author_profile_link, _class="item")
        else:
            div_author = a(href=self.author_profile_link, _class="item", target="_blank")
        
        # Create the <span/> that will contain the author and their profile link.
        div_author += span(raw(get_icons_svg("user")), _class="item-icon")
        div_author += span(self.author, _class="item-text")
        
        if self.category_link == "#":
        # "#" means that the link points to itself, so it's not necessary to
        # have it open in a new tab / window when clicked.
            div_category = a(href=self.category_link, _class="item")
        else:
            div_category = a(href=self.category_link, _class="item", target="_blank")
        
        # Create the <span/> that will contain the category and its link.
        div_category += span(raw(get_icons_svg("tag")), _class="item-icon")
        div_category += span(self.category, _class="item-text")

        # Create the <span/> that will contain the read time of the story.
        div_timer = span(_class="item")
        div_timer += span(raw(get_icons_svg("timer")), _class="item-icon")
        div_timer += span(str(readtime.of_html(self.story_html)), _class="item-text")

        div_details.add(div_author)
        div_details.add(div_category)
        div_details.add(div_timer)

        # Add the author, category, and read time <div/> to the HTML file.
        d += div_details 

        # Add the HTML format of the story to the HTML file. raw() ensures that
        # no further processing is done on the story_html before adding it to
        # the HTML file.
        div_content = div(_class="content")
        div_content.add(hr())
        div_content.add(raw(self.story_html))
        div_content.add(hr())
        d += div_content

        # Fetch the required JavaScript file.
        d_script_file = "script.js"
        d_script = ""
        with open(d_script_file, "r") as f:
            d_script = f.read()

        # Write the JavaScript at the end of <body/> of the HTML file.
        d += script(raw(d_script))

        # Write the HTML file to disk in "utf-8". "Pretty" ensures that the 
        # rendering is done in a more human-readable format.
        with open(os.path.join("exported", file_name), "w", encoding="utf-8") as f:
            f.write(d.render(pretty=True))

        return file_name
    # ---   
# ---

# Retrieves icons in SVG format.
# Thanks to https://materialdesignicons.com/
def get_icons_svg(type="user"):
    """Icons in SVG format"""

    svg_tag = """<svg style="width:24px;height:24px" viewBox="0 0 24 24">
                  <path fill="currentColor" 
                  d="M21.41 11.58L12.41 2.58A2 2 0 0 0 11 2H4A2 2 0 0 0 2 4V11A2 
                  2 0 0 0 2.59 12.42L11.59 21.42A2 2 0 0 0 13 22A2 2 0 0 0 14.41 
                  21.41L21.41 14.41A2 2 0 0 0 22 13A2 2 0 0 0 21.41 11.58M13 20L4 
                  11V4H11L20 13M6.5 5A1.5 1.5 0 1 1 5 6.5A1.5 1.5 0 0 1 6.5 5Z" />
                 </svg>"""

    svg_user = """<svg style="width:24px;height:24px" viewBox="0 0 24 24">
                   <path fill="currentColor" 
                   d="M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 
                   12,4M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z" />
                  </svg>"""

    svg_timer_sand = """<svg style="width:24px;height:24px" viewBox="0 0 24 24">
                         <path fill="currentColor" d="M6,2H18V8H18V8L14,12L18,
                         16V16H18V22H6V16H6V16L10,12L6,8V8H6V2M16,16.5L12,12.5L8,
                         16.5V20H16V16.5M12,11.5L16,7.5V4H8V7.5L12,11.5M10,
                         6H14V6.75L12,8.75L10,6.75V6Z" />
                        </svg>"""

    if type == "user":
        return svg_user
    elif type == "tag":
        return svg_tag
    elif type == "timer":
        return svg_timer_sand
# ---

# Retrieves the GUI layout.
def get_window_layout():
    # Layout for gui window.
    layout = [  [sg.Push(), sg.Text(text="Story / Article Saver", font="DEFAULT 16"), sg.Push()],
                [sg.Push(), sg.Text(text="Utility to save a story / article offline in HTML with light/dark mode."), sg.Push()],
                [sg.Push(), sg.Text(text="(*) mandatory fields")],
                [sg.Push(), sg.Text("Title*"), sg.InputText(key="-TITLE-", tooltip=" Main title of the story ")],
                [sg.Push(), sg.Text("Description"), sg.InputText(key="-DESCRIPTION-", tooltip=" Short tagline or summary ")],
                [sg.Push(), sg.Text("Author*"), sg.InputText(key="-AUTHOR-", tooltip=" Author ")],
                [sg.Push(), sg.Text("Publisher*"), sg.InputText(key="-PUBLISHER-", tooltip=" Publisher / website host ")],
                [sg.Push(), sg.Text("Category"), sg.InputText(key="-CATEGORY-", tooltip=" Category ")],
                [sg.Push(), sg.Text("Link to Story"), sg.InputText(key="-STORY LINK-", tooltip=" Direct link to the story ")],
                [sg.Push(), sg.Text("Link to Author Profile"), sg.InputText(key="-AUTHOR PROFILE LINK-", tooltip=" Direct link to the author profile ")],
                [sg.Push(), sg.Text("Link to Category"), sg.InputText(key="-CATEGORY LINK-", tooltip=" Direct link to the category of the story ")],
                [sg.Push(), sg.Text("Story*"), sg.Multiline(key="-STORY-", tooltip=" The Story content ", size=(43,10), autoscroll=True)],
                [sg.Push(), sg.Checkbox("Story is in Markdown format", key="-MARKDOWN-", default=True,
                  tooltip=" If selected, the text in Story field will be considered to be in the Markdown format ")],
                [sg.Push(), sg.Text(""), sg.Button("Save"), sg.Button("Reset", tooltip=" Reset all fields to blank "), sg.Button("Cancel")],
                [sg.Push(), sg.Multiline("", size=(73,3), key="-MESSAGE-", 
                 disabled=True, autoscroll=True, background_color="#eee", font=("Consolas", 8))] ]

    return layout
# ---

# Main function.
def main():
    """Main function"""

    # Set the theme of the GUI.
    sg.theme("SystemDefaultForReal")

    # Create the window.
    window = sg.Window("Story Saver", get_window_layout(), finalize=True)

    # Event loop to process "events" and get the "values" of the inputs.
    while True:
        event, values = window.read()
        
        if event == sg.WIN_CLOSED or event == "Cancel": 
            # if user closes window or clicks cancel.
            break
        
        # Initialize the story object with user provided values.
        story = Story()
        story.title = values["-TITLE-"]
        story.description = values["-DESCRIPTION-"]
        story.author = values["-AUTHOR-"]
        story.publisher = values["-PUBLISHER-"]
        story.category = values["-CATEGORY-"]
        story.story_link = values["-STORY LINK-"]
        story.author_profile_link = values["-AUTHOR PROFILE LINK-"]
        story.category_link = values["-CATEGORY LINK-"]
        story.story = values["-STORY-"]
        story.markdown = values["-MARKDOWN-"]

        try:
            if event == "Reset":
                window["-TITLE-"].update("")
                window["-DESCRIPTION-"].update("")
                window["-AUTHOR-"].update("")
                window["-PUBLISHER-"].update("")
                window["-CATEGORY-"].update("")
                window["-STORY LINK-"].update("")
                window["-AUTHOR PROFILE LINK-"].update("")
                window["-CATEGORY LINK-"].update("")
                window["-STORY-"].update("")
                window["-MARKDOWN-"].update(True)
                window["-TITLE-"].SetFocus()
                window["-MESSAGE-"].update("All values have been reset")
                continue

            elif event == "Save":
                file_name = story.save()
                if file_name == None:
                    window["-MESSAGE-"].update("Please fill all mandatory fields")
                else:
                    window["-MESSAGE-"].update("Saved to " + file_name)

        # Exceptions handling.
        except IndexError as eIndex:
            print("IndexError: " + str(eIndex))
            window["-MESSAGE-"].update("IndexError: " + str(eIndex))
        except TypeError as eType: 
            print("TypeError: " + str(eType))
            window["-MESSAGE-"].update("TypeError: " + str(eType))
        except UnicodeEncodeError as eUnicodeEncode:
            print("UnicodeEncodeError: " + str(eUnicodeEncode))
            window["-MESSAGE-"].update("UnicodeEncodeError: " + str(eUnicodeEncode))
        except AttributeError as eAttributeError:
            print("AttributeError: " + str(eAttributeError))
            window["-MESSAGE-"].update("AttributeError: " + str(eAttributeError))
        except Exception as eXception:
            print("Exception: ", str(eXception))
            window["-MESSAGE-"].update("Exception: ", str(eXception))
            sg.popup_error_with_traceback(f'An error happened.  Here is the info:', eXception)

    # Close the window once loop is broken.
    window.close()
# ---

# Main program starts.
if __name__ == "__main__":
    main()
# ------