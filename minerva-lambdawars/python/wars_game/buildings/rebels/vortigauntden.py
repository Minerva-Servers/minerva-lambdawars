from vmath import Vector, QAngle
from core.buildings import WarsBuildingInfo, UnitBaseFactory as BaseClass
from entities import entity

@entity('build_reb_vortigauntden', networked=True)
class RebelsVortigauntDen(BaseClass):
    # Settings
    autoconstruct = False
    buildtarget = Vector(0, -280, 32)
    buildangle = QAngle(0, 0, 0)
    customeyeoffset = Vector(0,0,96)
    
# Register unit
class VortigauntDenInfo(WarsBuildingInfo):
    name        = "build_reb_vortigauntden" 
    cls_name    = "build_reb_vortigauntden"
    image_name  = 'vgui/rebels/buildings/build_reb_vortigauntden'
    displayname = '#BuildRebVortigauntDen_Name'
    description = '#BuildRebVortigauntDen_Description'
    modelname = 'models/pg_props/pg_buildings/rebels/pg_reb_vortigauntden.mdl'
    explodemodel = 'models/pg_props/pg_buildings/rebels/pg_reb_vortigauntden_destruction.mdl'
    costs = [('requisition', 50), ('scrap', 50)]
    health = 800
    buildtime = 60.0
    techrequirements = ['build_reb_triagecenter']
    abilities   = {
        0 : 'unit_vortigaunt',
        1 : 'unit_antlion_small',
        4 : 'larvalextract_unlock',
        11 : 'cancel',
    }
    idleactivity = 'ACT_IDLE'
    # workactivity = 'ACT_WORK'
    explodeactivity = 'ACT_EXPLODE'
    constructionactivity = 'ACT_CONSTRUCTION'
    sound_select = 'build_reb_vortigauntden'
    sound_work = 'rebel_vortden_working'
    sound_death = 'build_generic_explode1'
    scale = 0.9
    explodeparticleeffect = 'building_explosion'
    explodeshake = (2, 10, 2, 512) # Amplitude, frequence, duration, radius
    sai_hint = WarsBuildingInfo.sai_hint | set(['sai_building_barracks', 'sai_building_vortden'])
    
# Register unit
class DestroyHQVortigauntDenInfo(VortigauntDenInfo):
    name        = "build_reb_vortigauntden_destroyhq"
    techrequirements = ['build_reb_triagecenter_destroyhq']
    abilities   = {
        0 : 'unit_vortigaunt',
        4 : 'larvalextract_unlock',
        11 : 'cancel',
    } 