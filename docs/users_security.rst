Manage Users
============
The Manage Users activities provides access to the user management workflows described below. These actions are only possible
if you have been granted required security points by your Team Admin. (Security point 810 is needed to activate users, and
830 and 840 are needed to modify non-admin and admin security points, respectively.)

Go to Admin > Manage Plate Templates in the navigation bar.

Viewing User Information
------------------------
Select the name of the user you wish to inspect. The following information is displayed:

#. username
#. Email address
#. Active - The user is only able to log in to the system if this box is checked.
#. Security points - A list of all security points granted to the uesr.

Activating a User
-----------------
All inactive users in your team will appear in the user list with an inactive icon:

   .. image:: /photos/users_security_inactive_icon.png
      :scale: 60 %
      :alt: Create sample
      :align: center

Select the desired user, and check the "Active" box.

   .. image:: /photos/users_security_active.png
      :scale: 60 %
      :alt: Create sample
      :align: center

Press "Update user" to save the changes, after configuring security points.

Configuring Security Points
---------------------------
Security points permit the user to access activities and perform actions.
Select the desired user, then open the "Security Points" dropdown menu. Check security points to grant them to the user.

   .. image:: /photos/users_security_secpoints.png
      :scale: 60 %
      :alt: Create sample
      :align: center

Press "Update user" to save the changes.

Granting Admin Privileges
-------------------------
A user can be granted admin privileges by being given admin security points by a user with the appropriate privileges to do so.

A user with 800 and 810 will be able to activate new and inactive users. They will not be able to inactivate
currently active users, which is regulated by security point 820.

The ability to modify security points of a user is granted by the following two security points:

 * 830 - permits modification of non-admin security points (all points below 500)
 * 840 - permits modification of admin security points (all points at and above 500)

Note that if a Team Admin grants 840 to another user, that user will have equivalent security to modify admin security points,
including the ability to remove administrative privileges from the first user.