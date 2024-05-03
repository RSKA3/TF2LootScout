config = {
    "log_file_path" : "/home/rasmus/Documents/projects/tf_valorizer/data/app.log",
    "database_file_path" : "/home/rasmus/Documents/projects/tf_valorizer/data/items.db",

    "tables" : {"item_table" : "stn_bot_items", 
                "new_item_table" : "new_stn_bot_items", 
                "valuable_item_table" : "valuable_stn_bot_items",
                "error_table" : "runs",
                "bots_table" : "bots"},
        
    "categories_to_parse" : ["genuines"],
    "valubable_sheens" : ["fire Horns", "tornado"],
    "valuable_killstreakers" : ["team shine", "villainous violet", "hot rod"],
    "valuable_aspects" : {"valuable_parts" : ["Dominations", "Damage Dealt", "Player Hits"],
                        "valuable_paints" : ['An Extraordinary Abundance of Tinge', 'A Distinctive Lack of Hue',
                                            'The Bitter Taste of Defeat and Lime', 'Pink as Hell', 'Team Spirit'],
                        "valuable_sheens" : ["fire Horns", "tornado"],
                        "valuable_killstreakers" : ["team shine", "villainous violet", "hot rod"]},
    "aspects" : {"parts" : ["Airborne Enemies Killed", "Heavies Killed", "Demomen Killed", "Revenge Kills", "Domination Kills", "Soldiers Killed", "Full Moon Kills", 
                            "Cloaked Spies Killed", "Scouts Killed", "Engineers Killed", "Robots Destroyed", "Low-Health Kills", "Halloween Kills", "Robots Destroyed During Halloween"
                            "Underwater Kills", "Snipers Killed", "Kills While Übercharged", "Pyros Killed", "Defender Kills", "Medics Killed", "Tanks Destroyed"
                            "Medics Killed That Have Full ÜberCharge", "Giant Robots Destroyed", "Kills During Victory Time", "Robot Spies Destroyed", "Unusual-Wearing Player Kills"
                            "Spies Killed", "Burning Enemy Kills", "Killstreaks Ended", "Damage Dealt", "Point-Blank Kills", "Full Health Kills", "Robot Scouts Destroyed"
                            "Taunting Player Kills", "Not Crit nor MiniCrit Kills", "Player Hits", "Gib Kills", "Buildings Destroyed", "Headshot Kills", "Projectiles Reflected"
                            "Allies Extinguished", "Posthumous Kills", "Critical Kills", "Kills While Explosive Jumping", "Sappers Destroyed", "Long-Distance Kills"
                            "Kills with a Taunt Attack", "Freezecam Taunt Appearances", "Fires Survived", "Kills", "Assists", "Allied Healing Done"]}
        }