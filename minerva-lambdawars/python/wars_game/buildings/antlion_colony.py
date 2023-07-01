from srcbase import *
from vmath import *
import random
from core.abilities import AbilityUpgrade
from core.buildings import WarsBuildingInfo, UnitBaseFactory as BaseClass
from .pheromone_marker import PheromoneMarkerBase
from entities import entity
import playermgr

@entity('build_ant_colony')
class AntlionColony(BaseClass, PheromoneMarkerBase):
    def __init__(self):
        BaseClass.__init__(self)
        PheromoneMarkerBase.__init__(self)        

    def Precache(self):    
        BaseClass.Precache(self)
        PheromoneMarkerBase.Precache(self)
        
    def Spawn(self):
        BaseClass.Spawn(self)
        PheromoneMarkerBase.Spawn(self)
        
    def UpdateOnRemove(self):
        BaseClass.UpdateOnRemove(self)
        PheromoneMarkerBase.UpdateOnRemove(self)
        
    def Event_Killed(self, info):
        BaseClass.Event_Killed(self, info)
        PheromoneMarkerBase.Event_Killed(self, info)
        
    # Settings     
    buildtarget = Vector(0, -256, 96.0)
    buildangle = QAngle(0, 0, 0)
    generationtype = 1
    customeyeoffset = Vector(0,0,150)
    
# Register unit
class AntlionColonyInfo(WarsBuildingInfo):
    name        = 'build_ant_colony'
    cls_name    = 'build_ant_colony'
    image_name  = "vgui/minervawars/antlions/buildings/build_ant_colony.vmt"
    abilities   = {
        0 : 'unit_antlionworker',
        1 : 'unit_antlionguard',
        2 : 'unit_antlionguardcavern',
        3 : 'tier2_research',
    }
    health = 4000
    modelname = 'models/props_wasteland/antlionhill.mdl'
    displayname = 'Antlion Colony'
    description = '#AntlionColony_Description'
    providespopulation = 11
    generateresources = {'type' : 'grubs', 'amount' : 1.0, 'interval' : 10}
    costs = [('grubs', 50)]
    sai_hint = WarsBuildingInfo.sai_hint | set(['sai_building_hq', 'sai_scrap_collection', 'sai_building_population'])
    buildtime = 60

class MiniAntlionColonyInfo(AntlionColonyInfo):
    name        = 'build_ant_minicolony'
    image_name  = "vgui/minervawars/antlions/buildings/build_ant_colony.vmt"
    abilities   = {
        0 : 'unit_antlionworker',
    }
    health = 1500
    modelname = 'models/props_wasteland/antlionhill.mdl'
    displayname = 'Antlion Mini-Colony'
    description = ''
    providespopulation = 8
    generateresources = {'type' : 'grubs', 'amount' : 1.0, 'interval' : 60}
    costs = [('grubs', 40)]
    scale = 0.5
    sai_hint = WarsBuildingInfo.sai_hint | set(['sai_building_barracks', 'sai_scrap_collection', 'sai_building_population'])
    buildtime = 50
    
class Tier2UpgradeInfo(AbilityUpgrade):
    name = 'tier2_research'
    displayname = '#AbilityTier2Research_Name'
    image_name = 'vgui/abilities/tier2.vmt'
    description = '#AbilityTier2Research_Description'
    buildtime = 120.0
    costs = [('requisition', 120), ('grubs', 10)]
    successorability = 'tier3_research'
    
class Tier3UpgradeInfo(AbilityUpgrade):
    name = 'tier3_research'
    image_name = 'vgui/abilities/tier3.vmt'
    displayname = '#AbilityTier3Research_Name'
    description = '#AbilityTier3Research_Description'
    buildtime = 180.0
    costs = [('requisition', 180), ('grubs', 20)]

class MissionAntlionColonyInfo(AntlionColonyInfo):
    name = 'mission_build_ant_colony'
    abilities   = {                      
        0 : 'unit_antlion_small',
        1 : 'mission_unit_antlionguard',
    }
    scale = 0.7
    health = 900