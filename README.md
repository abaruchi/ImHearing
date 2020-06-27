# Im Hearing

[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.svg?v=103)](https://opensource.org/licenses/mit-license.php)

## Contents
1. [Introduction](#introduction)
2. [How to Install & Use](#how-to-install-and-use)
3. [Implementation Details](#implementation-details)
4. [How to Contribute](#How-to-contribute)
5. [References](#references)

## Introduction

This is a personal project, in which I put in practice things like:

* Usage of Posix Threads
* Keep tracking of data stored in Cloud using local DB
* Usage of ORM

Also, Im using my RaspberryPi and a Mic to store environment sounds. The thing is
my Raspberry doesnt have so much storage available and, of course, I didn't want
to loose my records due to storage problems. So, my idea was to after a given 
number of records (or after a given amount of storage usage), the script must
archive the records and upload it to the Cloud (some cheap object store).

Of course, this idea had some problems, for example, my main concerns:

* If I want a record from a specific day of the last month, how do I get it?
* During the upload to the cloud, supposing it takes several minutes, how do I keep recording?

For the first question, I created a database using SQLite using Pony ORM to keep 
tracking of the records. So, you can just query for a specific day and it will
return the archive URL path to download. The second question I used Posix Threads 
with QUEUE (producer-consumer strategy). So when I reach the given amount of storage
or a number of records a task is added to a queue and a thread consumes it (archive
and upload).

Well, again, this is just a personal project that I created to use some hardware
that I wasn't using (actually, the Raspiberry I was using, just the USB mic was idle). So,
it is not my intention to create anything professional here or commercial, this is 
just fun.


## How to Install and Use

---
**NOTE**

Before installing, make sure ALSA is properly configured and working. For
more details, please refer to item 1 in [References](#references).

---

Before installing, be aware that Im using Python 3.7 to develop. For now, I don't think
it is a problem, since this project is not using any `asyncio` new features, but
in future versions, my intention is to use it. Let's start:

Installing the script is easy, the first step is to clone (or download) it from
the Git:

```bash
git clone https://github.com/abaruchi/ImHearing
```

After that, install the requirements:

```bash
pip install -r requirements.txt
```

Create the `config.ini` file using the [configuration template](config_example.ini):

```bash
cp -p config_example.ini config.ini
```

Change the parameters according to your needs. Note that this file contains 
a configuration to AWS, so make sure you configured AWS Cli (refer to item 2
in [References](#references)). 


## References

1. [Configuring MIC in RaspiberryPI](https://raspberrytips.com/add-microphone-raspberry-pi/)
2. [Configuring AWS CLI in Linux](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
