#!/usr/bin/env python3

import json
import os
import base64
import re 
import sys

def CreateImageFolder(notebook_name):
    save_dir = "./"+notebook_name+"-images/"
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
        print("Directory " , save_dir ,  " Created ")
    return save_dir


def main():

    try:   
        notebook_name = sys.argv[1]
    except:
        print("Usage ./notebook_to_md.py filename.ipynb ")
        exit()

    notebook_name = notebook_name.replace(".ipynb","")

    try:
        notebook = open("./" + notebook_name + '.ipynb')
    except:
        print("Jupyter notebook not found.")
        print("Usage ./notebook_to_md.py filename.ipynb ")
        exit()
    notebook_name = notebook_name.replace(".ipynb","")
    md_notebook = open(notebook_name+'.md', "w")

    try:
        notebook_json = json.load(notebook)
    except:
        print("Notebook not correctly formatted.")
        exit()
  
    # cell list
    l = [cell for cell in notebook_json['cells']]

    #counter of the attachments to save them
    attachments_counter = 0

    for cell in l:
        
        # avoid table of content cells 
        if 'toc' in cell['metadata']:
            continue

        # if the cell have attachments save them in a folder 
        # and map its name in a dictionary {name:new_saved_name}
        if 'attachments' in cell:

            # create a dictionary (cells use always the same name, so we create new names to save the images)
            cell_attachments_names = {}

            for att in cell['attachments']:

                #create the name for the new image
                image_name = notebook_name+"-image"+str(attachments_counter)+'.png'

                # add new name to the dictionary of name:new_saved_name
                cell_attachments_names[att] = image_name 

                #create the image folder
                image_folder = CreateImageFolder(notebook_name)

                #get image data (base64)
                image = cell['attachments'][att]['image/png']
                
                #get image bytes
                image = base64.b64decode(image)
                
                #save the image in the directory
                image_file = open(image_folder+"/"+image_name, "wb")
                image_file.write(image)
                image_file.close()

                # increment the counter for the image names
                attachments_counter+=1

        # get the cell text and save in the md file
        if 'source' in cell:

            # if the cell is code add the markdown code syntax before the text
            if cell['cell_type']=="code":
                md_notebook.writelines("```\n")

            # for every text part in the cell (the cell has several text parts)
            for text in cell['source']:
                
                new_text = text

                # if there is attachment in the cell
                if 'attachment' in new_text:
                    try:
                        # get the attachment names
                        image_names = re.findall(r"(?<=attachment:)(.*?)(?=\))",text) #was (?<=!\[)(.*?)(?=\])
                        
                        # get the name in the square brackets
                        squared_bracket_names = re.findall(r"(?<=!\[)(.*?)(?=\])",text)

                        for img,s_img in zip(image_names,squared_bracket_names):
                            try:
                                # get the new name of the image (how it was saved)
                                new_image_name = cell_attachments_names[img]

                                # replace the image attachment for notebooks to the image format for md file
                                new_text = new_text.replace("!["+s_img+"](attachment:"+img+")","![["+CreateImageFolder(notebook_name)+new_image_name+"]]")

                            except:
                                print("error with:" + cell_attachments_names[img])

                            cell_attachments_names[img]
                    except: #it was just a word
                        None

                # write the text in the md
                md_notebook.writelines(new_text)
                
            # if the cell is code add the markdown code syntax after the text
            if cell['cell_type']=="code":
                md_notebook.writelines("\n```")


            md_notebook.writelines("\n\n") # new line at the end of a cell

    md_notebook.close()
    print("Done. Markdown file saved as "+notebook_name+".md. Images saved in folder "+notebook_name+"-images.")

if __name__ == "__main__":
    main()
