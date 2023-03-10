# Hunt-Match-Tracker
![https://www.huntshowdown.com/assets/img/logo-nav.png](https://www.huntshowdown.com/assets/img/logo-nav.png)

**Hunt-Match-Tracker** is a tool which automatically checks the attributes.xml produced by the game [Hund: Showdown by Crytek](https://www.huntshowdown.com/) in the installation path. In this file are many attributes stored about the player and last match. (Bloodline, MMR, Map, Bosses, etc...)

## How does this work?

### Find attributes.xml
We request the Steam installation path from the Windows Registry and look up informations about the Steam Game Libraries.  

```mermaid
stateDiagram-v2
    WinRegistry --> SteamInstall : Look up Steam path
    SteamInstall --> SteamGameLib : Get Steam libraries
    SteamGameLib --> HuntShowdownInstall : Get Hunt install path
    HuntShowdownInstall --> Attributes.XML : Find attributes.xml file
    Attributes.XML --> Monitoring : Monitor
```
### Monitoring attributes.xml
Every 60 seconds we read the attributes file and compare the old and  new match hash (SHA-256 Hash from all player ids ordered and concatened). 
- If a new hash is found we will process the file. 
- If not we skip the processing.

```mermaid
stateDiagram-v2
    Attributes.xml --> JSON : Transform XML into JSON
    JSON --> Parsing : Create data objects 
    Parsing --> Message : Create message from data objects
    Message --> Topic : Push message to KAFKA cluster
    Topic --> ConsumerInsights: Deliver realtime data to Durid
    Topic --> DataWarehouse : Presistant data storage to Citus
```

# FAQ
> Where can I download the tool?

Pleas head to the [release page](https://github.com/gamepace/Hunt-Match-Tracker/releases) and download the latest executable!

> Why should I use this tool?

This tool extracts player data and pushes it to the Gamepace Data Warehouse. (In the future we will provide a web interface with statistics about your profile.) 

> Is this tool safe?

This tool should be safe. If you are unsure please read through the code or raise an issue [here](https://github.com/gamepace/Hunt-Match-Tracker/issues)!

> Can I get banned for using this tool?

We do not directly access the game process nor memory and should **not** trigger any EAC actions. However we have no official response by Crytek and therefore the use of this tool is **YOUR OWN RISK**!


> What is Gamepace?

Gamepace is a project that maintains tools to analyze games statistics. Gamepace is a project the host the data infrastructure such as Databases, APIs, Messaging Services and provide tools (open and closed source) for players to monitor progress and statistics for free. Feel free to contact [kggx via Twitter](https://twitter.com/kgg_x3)!

> I have a general question.

Please raise a issue [here](https://github.com/gamepace/Hunt-Match-Tracker/issues)!

# Disclaimer
We at Gamepace are not affiliated with Crytek or Hunt: Showdown in any case.

# Contributors
<a href="https://github.com/gamepace/Hunt-Match-Tracker/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=gamepace/Hunt-Match-Tracker" />
</a>