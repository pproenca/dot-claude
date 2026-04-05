# Creating a Core Data model

_Article_

> Source: https://developer.apple.com/documentation/coredata/creating_a_core_data_model

Define your app’s object structure with a data model file.

### Overview

The first step in working with Core Data is to create a data model file to define the structure of your app’s objects, including their object types, properties, and relationships.

You can add a Core Data model file to your Xcode project when you create the project, or you can add it to an existing project.

#### Add Core Data to a New Xcode Project

In the dialog for creating a new project, select the Use Core Data checkbox, and click Next.

[image: Screenshot showing the Use Core Data checkbox in the options for creating a new Xcode project. The checkbox appears after the language dropdown, and before the checkboxes for including Unit Tests and UI Tests.]

The resulting project includes an `.xcdatamodeld` file.

[image: Screenshot showing the .xcdatamodeld file highlighted in the project navigator.]

#### Add a Core Data Model to an Existing Project

Choose File > New > File and select the iOS platform tab. Scroll down to the Core Data section, select Data Model, and click Next.

[image: Screenshot showing the Data Model template in the Core Data section of the file template chooser.]

Name your model file, select its group and targets, and click Create.

[image: Screenshot showing the dialog for saving a data model file. The filename is selected and immediately editable.]

Xcode adds an `.xcdatamodeld` file with the specified name to your project.

[image: Screenshot of Xcode showing the new model file selected in the project navigator.]
