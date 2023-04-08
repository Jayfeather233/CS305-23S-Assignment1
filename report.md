<center>
    <h1>
        CS305 Program Assignment 1
    </h1>
</center>

### Testing Script:

![image-20230325203444000](image-20230325203444000.png)

![image-20230327204126959](image-20230327204126959.png)

### Additional

#### User login contorl

In `PASS` command, I will check if the username and password match the record. A bool: `is_login` is set to be True/False. I store the username and password in a `dict` variable in memory, and a `json` file in hard disk.

To ensure the security, I give every user a random salt to encode his password with sha256.

If not login, I will not provide any file command to this user.

![image-20230325210043333](image-20230325210043333.png)

#### User privilege control

The `dict` that store the user will be:

`username: tuple(salt, passwd_in_sha256, privilege_bit)`

if privilege bit is 1, then he/she can store file in the server. Otherwise he/she can only download.

![image-20230325210137108](image-20230325210137108.png)

#### More commands

`SIZE` that return a file's size

`TYPE` that specify file transmit type. `I` for binary, `A` for ASCII, `E` for EBCDIC

`SYST` that return the system type

![image-20230327212925790](image-20230327212925790.png)

![image-20230327212836363](image-20230327212836363.png)

#### not ftp but in server

When running the server, you could input `user` to create an new user; input `end` to shutdown and close every connection.

Input_process and ftp_server are running in different thread.

![image-20230325210217179](image-20230325210217179.png)