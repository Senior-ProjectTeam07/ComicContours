**login_page.py**

Security Features Implemented:

1. Ensuring Password Security:

Bcrypt Hashing: To ensure the security of user passwords we utilize the bcrypt algorithm for robust password hashing. This recognized method provides cryptographic strength, in password protection.

Salt Generation: For added security, Bcrypt automatically generates salts for each password. This significantly enhances the security measures in place.

2. Password Complexity Criteria:

Complexity Validation: To ensure the security of your password certain complexity criteria need to be met. These criteria include checking for a length the presence of both uppercase and lowercase letters, numbers and special characters.

Validation on the Users End: Before encrypting and saving passwords our system verifies their complexity to minimize the risk of passwords.

3. Interacting with a Secure Database:

SQLite Database: Our code utilizes a database to store user data. This choice ensures that we have an easy method of managing user information.

SQL attack prevention: To safeguard against SQL attacks we employed queries. This security measure helps protect our system from web vulnerabilities.

4. Record keeping:

Error and Access Logging: The code keeps track of activities and errors which is essential, for monitoring and identifying potential security concerns.

5. Dealing with Errors:

Error Management: A focus, on error management; The code has implemented efficient error handling mechanisms to effectively handle and record exceptions especially when it comes to database operations. This does not improve the reliability of the system. Also enhances its security.

6. Security of the User Interface:

Notifying Users about Authentication Failures: The code offers users feedback when their login attempts fail such, as due, to credentials while safeguarding against disclosing information that could potentially assist malicious activities.

Sources Referenced:

https://pypi.org/project/bcrypt/
https://docs.python.org/3/library/sqlite3.html
https://docs.python.org/3/library/logging.html
https://docs.python.org/3/library/re.html
https://docs.python.org/3/
https://www.geeksforgeeks.org/hashing-passwords-in-python-with-bcrypt/
https://www.tutorialspoint.com/hashing-passwords-in-python-with-bcrypt
https://stackoverflow.com/questions/41283541/using-bcrypt-password-hashing-for-user-authentication
https://realpython.com/python-sqlite-sqlalchemy/
https://www.youtube.com/watch?v=gdDI_GhIRGo


**forgotpassword_page.py**

1. Ensuring Database Security:

SQL Database: Our code uses SQLite, a database technology to store user data.

Error Handling: To maintain stability and security we have implemented error handling mechanisms during interactions, with the database.

2. Making Password Reset Easy via Email:

STMP: To facilitate password resets securely we utilize the SMTP protocol for email communication.

Email Validation: We employ regex-based validation to ensure that the email provided for password reset follows the format.

3. User Friendly Interface and Prompt Feedback:

Feedback to User: Immediate feedback is provided to users for actions such as entering an email format or attempting to log in with an existent account.

4. Logging and Monitoring Activities:

Logging: We have incorporated logging functionality, into our system to monitor user management activities effectively and troubleshoot any issues that may arise.

5. Password Reset Process:

User Verification: Before initiating the password reset process, we verify the identity of the user by matching their name and email address.

Email Reset Link: Once verified a secure password reset link is sent to their registered email address so they can easily reset their password.

Sources Referenced:

https://docs.python.org/3/library/tkinter.html
https://docs.python.org/3/library/sqlite3.html
https://docs.python.org/3/library/smtplib.html
https://docs.python.org/3/library/email.mime.html#email.mime.text.MIMEText
https://docs.python.org/3/library/re.html
https://docs.python.org/3/library/logging.html


**createuser_page.py**

1. Ensuring Password Security:

Bcrypt Hashing: To safeguard user passwords our system utilizes bcrypt hashing, which encrypts passwords and prevents them from being stored in text. Additionally, bcrypt automatically adds a salt, to each password hash making identical passwords have distinct hashes. 

Password Strength: We also enforce password strength by requiring a combination of characters, numbers, special symbols and a minimum length to ensure security.

2. Validating Email Addresses:

Email Verification: To maintain the integrity of user data we employ expressions to validate the format of email addresses provided during registration.

3. Reliable Database Operations:

SQL Database: For storing user data, we used database technology due to its reliability. This ensures secure storage of user information.

4. User Friendly Interface with Real Time Feedback:

User Feedback: Users receive feedback for actions such as entering information or successfully creating an account.

5. Ensuring a Secure Account Creation Process

Data Verification: Before creating an account, our system performs validation checks, on all user inputs including name, email address and password to ensure correctness and strength.

Preventing Duplicate Accounts: Our code checks for any users who already have the email to avoid creating accounts.

Sources Referenced:

https://docs.python.org/3/library/tkinter.html
https://pypi.org/project/bcrypt/
https://docs.python.org/3/library/sqlite3.html
https://docs.python.org/3/library/re.html
https://docs.python.org/3/library/logging.html
