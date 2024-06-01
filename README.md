# Channels
**INFO**
### [#announcements](announcements.md)
### [#yuzu-updates](yuzu-updates.md)
### [#android-updates](index-android-updates/0.md)

**COMMUNITY CONTENT**
### [#media](media.md)
### [#game-mods](game-mods.md)
#

# The Yuzu Discord Archive
This is a backup of a few important channels from the Yuzu Discord server, the backup was started a few days after the server went into lockdown and was completed around March 9th, 2024. The server has now been deleted and is not longer accessible outside of archives like this.

Almost every game mod sent in the *\#game-mods* channel (with the extensions .zip, .rar, .7z, .txt, and .pchtxt) and every file in *\#media* are present in this archive, exceptions being random messages and attachments that were deleted during the backup.

All attachments are hosted on an AWS bucket and cannot be found in this repository, but a link to each is provided in the appropriate message since all files combined is over 60GB.

# How this was done (and why)
Sometime after it was revealed that Tropic Haze (Yuzu team) was in a lawsuit with Nintendo, I woke up late in the morning and saw a ping notification from the Yuzu Discord server. I almost wanted to fear the worst, but I thought maybe it was an update on how they're going to challenge the lawsuit, or maybe it was just a new Yuzu version with some important new feature.
I immediately checked the \#announcements channel, still in bed, and saw this:\

"*Hello yuz-ers and Citra fans:
We write today to inform you that yuzu and yuzu’s support of Citra are being discontinued, effective immediately.*"

At first I panicked and went to the \#general channel, only to find it was read only and had a *lot* of spam from new users and upset yuz-ers. I then checked every other channel to see if there were any left open, of which there were none.

I then remembered I had made a Python script a few months back to scrape all messages of a single user in a server, because I had planned to make a text generative AI bot from their (admittedly slightly unhinged) messages. I hopped on my computer and modified that code to read from all users in a given channel in the Yuzu server. I made some searches on the Discord message search bar, and found that, while some channels had *way* too many messages and files to back up (\#general, discussion channels, etc.) some of them had a small enough amounts of messages to be archived in only a few hours. 

Throughout almost the entire day, I spent time improving and testing my code to make sure every last message I needed was being preserved correctly. I also made sure to make small backups of messages and files as I went, just in case the server suddenly disappeared. Almost a week went by and the server had not gone down, and by then I had pretty much archived all of the channels you see here. 

I then improved and parsed the messages every so often, and started looking into ways to put this repository on a Git hosting service. This was *very* difficult to figure out, because even with GitHub Pro, I can only ever make a repository as big as 2GB. It's easy enough to host an FTP or Samba server locally and maybe a little harder to make it public, but this poses security risks for me and my network. Since *I* would be the one hosting it, *anyone* would be able to get my public IP address, which would allow someone to get my rough geographic location and potentially compromise my network. Even with a VPN, I would still potentially have a lot of network traffic from people trying to access it. I tried hosting it on Google Cloud Source Repositories, and then realized you can't actually make your repos public without whitelisting people manually.

Eventually the server disappeared from my server list, about a month after they caved under the lawsuit and paid Nintendo $2.4M. I decided to take a month or so off to work on other projects and live my life. In late May, I stumbled across Amazon's AWS CodeCommit service, which allows you to store a Git repo on their servers. This had the same problem as the Google service I mentioned in the last paragraph, but then I had a better idea; I could host the repo on GitHub with only the message data (~40MB) while hosting the files on a public AWS bucket, which is basically a cloud storage container with advanced permission settings among other things. Then I could link each file mentioned in the messages hosted on GitHub to the matching link on my AWS bucket.

This seemed a little impractical at first, but was easy enough to implement, all I would have to do is change my message parsing code to embed the AWS file link instead of the relative repository file path. In only a couple days I had uploaded my files to a private bucket, made it public, and then changed the message parsing code to link to the corresponding attachments in the bucket.

And here I am now (or rather May 31st, 2024) typing this long ass section that may as well be an autobiography. The AWS bucket is public, the GitHub repo contains every message I could archive before the shutdown, and now it's time to make this repository public!

## "index" folders
These are the pages of messages sent in the corresponding channel, each page contains about 100 messages.

## "pages" folders
This is the raw JSON data scraped from the server, it includes a lot of other variables that aren't included in the parsed Markdown files. (User IDs, avatar numbers, flags, etc.)

## "tools" folder
This contains the Python scripts I used to scrape the files and messages from Discord and reformat them into Markdown, I don't recommend using them as they were written very hastily and won't be able to pull messages from the Yuzu Discord since it's been deleted.
