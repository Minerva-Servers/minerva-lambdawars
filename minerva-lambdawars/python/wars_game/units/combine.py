from vmath import Vector
from core.abilities import AbilityUpgrade, AbilityUpgradeValue
from core.units import UnitInfo, UnitBaseCombatHuman as BaseClass, EventHandlerAnimation
from core.units.abilities import AbilityTransformUnit
from fields import BooleanField, UpgradeField
from entities import entity, Activity
import ndebugoverlay

if isserver:
    from animation import Animevent
    from unit_helper import BaseAnimEventHandler, TossGrenadeAnimEventHandler

@entity('unit_combine', networked=True)
class UnitCombine(BaseClass):
    """ Combine soldier. """
    if isserver:
        def DeathSound(self):
            self.expresser.SpeakRawSentence('COMBINE_DIE', 0.0)

    def OnTakeDamage(self, dmginfo):
        if self.lasttakedamage and self.health > 0 and dmginfo.GetDamage() > 0:
            self.EmitSound("unit_combine_hurt")
        return super().OnTakeDamage(dmginfo)
            
    def Spawn(self):
        super().Spawn()
        
        self.animstate.usecombatstate = True
        
        if isserver:
            self.UpdateSoldierSkin(self.activeweapon)
                
    if isserver:
        def OnUnitTypeChanged(self, oldunittype):
            super().OnUnitTypeChanged(oldunittype)
            
            self.UpdateSoldierSkin(self.activeweapon)
                
        def Weapon_Switch(self, weapon, viewmodelindex=0):
            rv = super().Weapon_Switch(weapon, viewmodelindex)
            if not rv:
                return False
                
            self.UpdateSoldierSkin(weapon)
            return True
            
        def Weapon_Equip(self, weapon):
            super().Weapon_Equip(weapon)
            
            self.UpdateSoldierSkin(weapon)
            
    def UpdateSoldierSkin(self, weapon):
        if not isserver or not weapon:
            return
            
        if weapon.GetClassname() == 'weapon_shotgun':
            self.skin = self.COMBINE_SKIN_SHOTGUNNER
        else:
            self.skin = self.COMBINE_SKIN_DEFAULT

    # Anim event handlers
    if isserver:
        def GrenadeInRangeLOSCheck(self, targetpos, target=None):
            startpos = Vector()
            self.GetAttachment("lefthand", startpos)
            
            handler = self.aetable[self.COMBINE_AE_GREN_TOSS]
            
            tossvel = Vector()
            if not handler.GetTossVector(self, startpos, targetpos, self.CalculateIgnoreOwnerCollisionGroup(), tossvel):
                return False
                
            return True
                
        class CombineThrowGrenade(TossGrenadeAnimEventHandler):
            def HandleEvent(self, unit, event):
                abi = unit.grenadeability
                if not abi:
                    return
                    
                if abi.grenadeclsname:
                    self.SetGrenadeClass(abi.grenadeclsname)

                startpos = Vector()
                unit.GetAttachment("lefthand", startpos)

                targetpos = abi.throwtarget.GetAbsOrigin() if abi.throwtarget else abi.throwtargetpos

                #UTIL_PredictedPosition(enemy, 0.5, targetpos) 

                grenade = self.TossGrenade(unit, startpos, targetpos, unit.CalculateIgnoreOwnerCollisionGroup())

                if grenade:
                    abi.OnGrenadeThrowed(unit, grenade)
                    grenade.SetVelocity(grenade.GetAbsVelocity(), Vector(0, 0, 0))
                    grenade.SetTimer( 2.5, 2.5 - grenade.FRAG_GRENADE_WARN_TIME ) #grenade detonation time (gtime)
                    
    #customeyeoffset = Vector(0, 0, 60)
    
    COMBINE_SKIN_DEFAULT = 0
    COMBINE_SKIN_SHOTGUNNER = 1
    
    COMBINE_GRENADE_THROW_SPEED = 650
    
    attackrange1act = Activity.ACT_RANGE_ATTACK_SMG1
    
    grenadeability = None
    canshootmove = True
    
    #test = UpgradeField(abilityname='testupgrade')
    
    # Activity list
    activitylist = list(BaseClass.activitylist)
    activitylist.extend([
        'ACT_IDLE_UNARMED',
        'ACT_WALK_UNARMED',
        'ACT_COMBINE_THROW_GRENADE',
    ])
    
    # Activity translation table
    acttables = dict(BaseClass.acttables)
    acttables.update( { 
        'default' : {
            Activity.ACT_IDLE : 'ACT_IDLE_UNARMED',
            Activity.ACT_WALK : 'ACT_WALK_UNARMED',
            Activity.ACT_RUN : Activity.ACT_RUN_AIM_RIFLE,
            Activity.ACT_MP_JUMP : Activity.ACT_JUMP,
            Activity.ACT_MP_JUMP_FLOAT : Activity.ACT_JUMP,
            
            Activity.ACT_CROUCH : Activity.ACT_COVER,
            Activity.ACT_RUN_CROUCH : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_WALK_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_RUN_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_CROUCHIDLE_AIM_STIMULATED : Activity.ACT_RANGE_ATTACK_SMG1_LOW, 
        },
        'weapon_smg1' : {
            Activity.ACT_WALK : Activity.ACT_WALK_RIFLE,
            Activity.ACT_RUN : Activity.ACT_RUN_RIFLE,
            Activity.ACT_RANGE_ATTACK1 : Activity.ACT_RANGE_ATTACK_SMG1,
            Activity.ACT_MP_JUMP : Activity.ACT_JUMP,
            Activity.ACT_MP_JUMP_FLOAT : Activity.ACT_JUMP,
            
            Activity.ACT_CROUCH : Activity.ACT_COVER,
            Activity.ACT_RUN_CROUCH : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_WALK_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_RUN_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_CROUCHIDLE_AIM_STIMULATED : Activity.ACT_RANGE_ATTACK_SMG1_LOW, 
            
            Activity.ACT_IDLE_AIM_AGITATED : Activity.ACT_RANGE_ATTACK_SMG1,
            Activity.ACT_WALK_AIM : Activity.ACT_WALK_AIM_RIFLE,
            Activity.ACT_RUN_AIM : Activity.ACT_RUN_AIM_RIFLE,
        },
        'weapon_shotgun' : {
            Activity.ACT_WALK : Activity.ACT_WALK_RIFLE,
            Activity.ACT_RUN : Activity.ACT_RUN_RIFLE,
            Activity.ACT_RANGE_ATTACK1 : Activity.ACT_RANGE_ATTACK_SHOTGUN,
            Activity.ACT_MP_JUMP : Activity.ACT_JUMP,
            Activity.ACT_MP_JUMP_FLOAT : Activity.ACT_JUMP,
            
            Activity.ACT_CROUCH : Activity.ACT_COVER,
            Activity.ACT_RUN_CROUCH : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_WALK_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_RUN_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_CROUCHIDLE_AIM_STIMULATED : Activity.ACT_RANGE_ATTACK_SHOTGUN_LOW, 
            
            Activity.ACT_IDLE_AIM_AGITATED : Activity.ACT_RANGE_ATTACK_SHOTGUN,
            Activity.ACT_WALK_AIM : Activity.ACT_WALK_AIM_SHOTGUN,
            Activity.ACT_RUN_AIM : Activity.ACT_RUN_AIM_SHOTGUN,
        },
        'weapon_pulse_shotgun': {
            Activity.ACT_WALK: Activity.ACT_WALK_RIFLE,
            Activity.ACT_RUN: Activity.ACT_RUN_RIFLE,
            Activity.ACT_RANGE_ATTACK1: Activity.ACT_RANGE_ATTACK_SHOTGUN,
            Activity.ACT_MP_JUMP: Activity.ACT_JUMP,
            Activity.ACT_MP_JUMP_FLOAT: Activity.ACT_JUMP,

            Activity.ACT_CROUCH: Activity.ACT_COVER,
            Activity.ACT_RUN_CROUCH: Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_WALK_CROUCH_AIM: Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_RUN_CROUCH_AIM: Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_CROUCHIDLE_AIM_STIMULATED: Activity.ACT_RANGE_ATTACK_SHOTGUN_LOW,

            Activity.ACT_IDLE_AIM_AGITATED: Activity.ACT_RANGE_ATTACK_SHOTGUN,
            Activity.ACT_WALK_AIM: Activity.ACT_WALK_AIM_SHOTGUN,
            Activity.ACT_RUN_AIM: Activity.ACT_RUN_AIM_SHOTGUN,
        },
        'weapon_ar2' : {
            Activity.ACT_WALK : Activity.ACT_WALK_RIFLE,
            Activity.ACT_RUN : Activity.ACT_RUN_RIFLE,
            Activity.ACT_RANGE_ATTACK1 : Activity.ACT_RANGE_ATTACK_AR2,
            Activity.ACT_MP_JUMP : Activity.ACT_JUMP,
            Activity.ACT_MP_JUMP_FLOAT : Activity.ACT_JUMP,
            
            Activity.ACT_CROUCH : Activity.ACT_COVER,
            Activity.ACT_RUN_CROUCH : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_WALK_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_RUN_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_CROUCHIDLE_AIM_STIMULATED : Activity.ACT_RANGE_ATTACK_AR2_LOW, 
            
            Activity.ACT_IDLE_AIM_AGITATED : Activity.ACT_RANGE_ATTACK_AR2,
            Activity.ACT_WALK_AIM : Activity.ACT_WALK_AIM_RIFLE,
            Activity.ACT_RUN_AIM : Activity.ACT_RUN_AIM_RIFLE,
        },
        
        'weapon_sniperrifle' : {
            Activity.ACT_WALK : Activity.ACT_WALK_RIFLE,
            Activity.ACT_RUN : Activity.ACT_RUN_RIFLE,
            Activity.ACT_RANGE_ATTACK1 : Activity.ACT_RANGE_ATTACK_AR2,
            Activity.ACT_MP_JUMP : Activity.ACT_JUMP,
            Activity.ACT_MP_JUMP_FLOAT : Activity.ACT_JUMP,
            
            Activity.ACT_CROUCH : Activity.ACT_COVER,
            Activity.ACT_RUN_CROUCH : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_WALK_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_RUN_CROUCH_AIM : Activity.ACT_RUN_CROUCH_RIFLE,
            Activity.ACT_CROUCHIDLE_AIM_STIMULATED : Activity.ACT_RANGE_ATTACK_AR2_LOW, 
            
            Activity.ACT_IDLE_AIM_AGITATED : Activity.ACT_RANGE_ATTACK_AR2,
            Activity.ACT_WALK_AIM : Activity.ACT_WALK_AIM_RIFLE,
            Activity.ACT_RUN_AIM : Activity.ACT_RUN_AIM_RIFLE,
        }
    } )
    
    # Events
    events = dict(BaseClass.events)
    events.update( {
        'ANIM_THROWGRENADE' : EventHandlerAnimation('ACT_COMBINE_THROW_GRENADE'),
    } )
    
    # Ability sounds
    abilitysounds = {
        'grenade': 'ability_combine_grenade',
        'deployturret': 'ability_combine_deployturret',
        'attackmove': 'ability_comb_attackmove',
        'holdposition': 'ability_comb_holdposition',
        'energyball': 'ability_combine_energyball',
    }

    if isserver:
        # Animation Events
        COMBINE_AE_GREN_TOSS = 7
        
        aetable = {
            Animevent.AE_NPC_BODYDROP_HEAVY: BaseAnimEventHandler(),
            COMBINE_AE_GREN_TOSS: CombineThrowGrenade('grenade_frag', COMBINE_GRENADE_THROW_SPEED),
        }
        
    # Anims
    class AnimStateClass(BaseClass.AnimStateClass):
        def __init__(self, outer, animconfig):
            super(UnitCombine.AnimStateClass, self).__init__(outer, animconfig)
            self.newjump = False

    buildtime = UpgradeField(abilityname='armycombine_tier_3', cppimplemented=True)
    energyballupgraded = UpgradeField(value=False, abilityname='combineball_upgrade')

@entity('unit_combinesniper', networked=True)
class UnitCombineSniper(UnitCombine):
    canshootmove = False
    insteadyposition = BooleanField(value=False, networked=True)
    maxhealth = UpgradeField(abilityname='combine_hp_upgrade', cppimplemented=True)
    health = UpgradeField(abilityname='combine_hp_upgrade', cppimplemented=True)
    
    def OnInCoverChanged(self):
        super().OnInCoverChanged()
        self.insteadyposition = self.in_cover
    
    if isserver:
        class BehaviorGenericClass(BaseClass.BehaviorGenericClass):
            class ActionHideSpot(BaseClass.BehaviorGenericClass.ActionHideSpot):
                # Don't break cover when targeting an enemy
                def OnNewOrder(self, order):
                    if order.type == order.ORDER_ENEMY:
                        return self.SuspendFor(self.behavior.ActionHideSpotAttack, 'Attacking enemy on order from cover/hold spot', order.target)

@entity('unit_combineheavy', networked=True)
class UnitCombineHeavy(UnitCombine):
    canshootmove = False
    regenerationtime = 0
    effecttime = 0
    soundtime = 0
    regeneration = False
    def UnitThink(self):
        super().UnitThink()
        if self.health < self.maxhealth and self.energy > 0 and self.regeneration:
            self.Regeneration()
    def Regeneration(self):
        while self.regenerationtime < gpGlobals.curtime:
            if not self.energy >= self.unitinfo.regenerationamount: 
                return
            if hasattr(self, 'EFFECT_DOHEAL'):
                self.DoAnimation(self.EFFECT_DOHEAL)
            self.regenerationtime = self.unitinfo.regenerationtime + gpGlobals.curtime
            self.health = min(self.health+regenerationamount, self.maxhealth) 
            self.TakeEnergy(energy)
    def ScaleDamageToAttributes(self, dmginfo, my_attributes):
        dmg_info = super().ScaleDamageToAttributes(dmginfo, my_attributes)
        olddmg = dmg_info.GetDamage()
        if dmg_info.GetDamage() <= self.energy:
            self.TakeEnergy(dmg_info.GetDamage())
            dmg_info.ScaleDamage(self.unitinfo.coef)
        elif dmg_info.GetDamage() > self.energy and self.energy > 0:
            dmg_info.ScaleDamage((1 + (self.unitinfo.coef - 1)*(self.energy/dmg_info.GetDamage()))) 
            self.TakeEnergy(self.energy)
        if dmg_info.GetDamage() != olddmg and dmg_info.GetDamage() < self.health:
            if self.effecttime < gpGlobals.curtime:
                self.effecttime = 0.50 + gpGlobals.curtime
                #if hasattr(self, 'EFFECT_DOSHIELD'):
                self.DoAnimation(self.EFFECT_DOSHIELD)
            if self.soundtime < gpGlobals.curtime:
                self.soundtime = 1.5 + gpGlobals.curtime
                self.EmitSound('combine_heavy_shield')
        return dmg_info
    if isserver:
        def Precache(self):
            super().Precache()
            
            self.PrecacheScriptSound( "combine_heavy_shield" )
            
# Register unit
class CombineSharedInfo(UnitInfo):
    cls_name = 'unit_combine'
    population = 1
    maxspeed = 214.78
    hulltype = 'HULL_HUMAN'
    attributes = ['light', 'bullet']
    infest_zombietype = 'unit_zombine' # For headcrab_infest ability
    cantakecover = True

class MechanicsCombine_Tier6(AbilityUpgradeValue): #TODO: replace with T1 upgrade
    name = 'mechanicscombine_tier_6'
    displayname = '#ArmyCombineT6Upgr_Name'
    description = '#ArmyCombineT6Upgr_Description'
    buildtime = 90.0
    costs = [('requisition', 30), ('power', 30)]
    upgradevalue = 240
    image_name = 'vgui/combine/abilities/combine_upgrade_tier_mid'
class CombineHPUpgrade(AbilityUpgradeValue): 
    name = 'combine_hp_upgrade'
    displayname = '#CombineHPUpgrade_Name'
    description = '#CombineHPUpgrade_Description'
    buildtime = 120.0
    costs = [[('requisition', 100), ('power', 80)], [('kills', 50)]]
    upgradevalue = 240
    image_name = 'vgui/combine/abilities/combine_hp_upgrade'

class ArmyCombine_Tier3(AbilityUpgradeValue):
    name = 'armycombine_tier_3'
    displayname = '#ArmyCombine_Tier_3_Name'
    description = '#ARmyCombine_Tier_3_Description'
    upgradevalue = 20

@entity('unit_combine_grenade_upgrade', networked=True)
class UnitCombineGrenadeUpgradeShared(UnitCombine):
    #def GetRequirements(self, requirements, info, player):
        #print('GetRequirements for', info.name)
        #if info.name == 'grenade_combine':
            #if not self.grenadeUnlocked:
                #requirements.add('needsupgrade')

    def OnGrenadeUnlockedChanged(self):
        self.UpdateTranslateActivityMap()
        self.UpdateAbilities()
        
    grenadeUnlocked = BooleanField(value=False, networked=True, clientchangecallback='OnGrenadeUnlockedChanged')
    maxhealth = UpgradeField(abilityname='combine_hp_upgrade', cppimplemented=True)
    health = UpgradeField(abilityname='combine_hp_upgrade', cppimplemented=True)
    buildtime = UpgradeField(abilityname='armycombine_tier_3', cppimplemented=True) #TODO: 'buildtime' doesn't work with UpgradeField?

class CombineInfo(CombineSharedInfo):
    name = 'unit_combine'
    cls_name = 'unit_combine_grenade_upgrade' # adds grenade unlock per unit this also needs the rebel_grenade_upgrade ability
    displayname = 'Combine Standard Soldier'
    description = ''
    image_name = 'vgui/combine/units/unit_combine'
    portrait = 'resource/portraits/combineSMG.bik'
    costs = [[('requisition', 25)], [('kills', 1)]]
    techrequirements = ['build_comb_armory']
    buildtime = 24.0
    health = 150
    maxspeed = 216.0
    viewdistance = 768
    attributes = ['medium']
    sound_select = 'unit_combine_select'
    sound_move = 'unit_combine_move'
    sound_attack = 'unit_combine_attack'
    modelname = 'models/combine_soldier.mdl'
   # tier = 2
    abilities = {
        0: 'grenade_combine',
        #1: 'combine_grenade_upgrade',
        5: 'combine_transform_sg',
        6: 'combine_transform_ar2',
        7: 'mountturret',
        8: 'attackmove',
        9: 'holdposition',
        10: 'patrol',
        -1: 'garrison',
    }
    weapons = ['weapon_smg1']

class UnlockCombTierMiddle(AbilityUpgrade):
    name = 'combine_upgrade_tier_mid'
    displayname = '#CombUpTierMid_Name'
    description = '#CombUpTierMid_Description'
    buildtime = 60.0
    costs = [('requisition', 40), ('power', 10)]

class CombineSGInfo(CombineInfo):
    name = 'unit_combine_sg'
    displayname = 'Combine Shotgunner Soldier'
    description = ''
    image_name = 'vgui/combine/units/unit_combine_sg'
    portrait = 'resource/portraits/combineShotgun.bik'
    costs = [[('requisition', 25), ('power', 5)], [('kills', 1)]]
    techrequirements = ['build_comb_armory','weaponsg_comb_unlock']
    attributes = ['medium']
    buildtime = 24.0
    health = 150
    maxspeed = 256.0
    viewdistance = 768
    sound_select = 'unit_combine_sg_select'
    sound_move = 'unit_combine_sg_move'
    sound_attack = 'unit_combine_sg_attack'
    modelname = 'models/combine_soldier.mdl'
   # tier = 2
    abilities = {
        0: 'grenade_combine',
        #1: 'combine_grenade_upgrade',
        7: 'mountturret',
        8: 'attackmove',
        9: 'holdposition',
        10: 'patrol',
        -1: 'garrison',
    }
    weapons = ['weapon_shotgun']

class CombineAR2Info(CombineInfo):
    name = 'unit_combine_ar2'
    displayname = 'Combine Amplified Soldier'
    description = ''
    image_name = 'vgui/combine/units/unit_combine_ar2'
    portrait = 'resource/portraits/combineAR2.bik'
    costs = [[('requisition', 25), ('power', 10)], [('kills', 2)]]
    techrequirements = ['build_comb_armory','weaponar2_comb_unlock']
    #techrequirements = ['build_comb_armory']
    buildtime = 28.0
    health = 150
    maxspeed = 184
    sensedistance = 1024.0
    viewdistance = 832
    #accuracy = 0.626
    attributes = ['medium']
    sound_select = 'unit_combine_ar2_select'
    sound_move = 'unit_combine_ar2_move'
    sound_attack = 'unit_combine_ar2_attack'
    modelname = 'models/combine_soldier.mdl'
   # tier = 2
    abilities = {
        0: 'grenade_combine',
        #1: 'combine_grenade_upgrade',
        7: 'mountturret',
        8: 'attackmove',
        9: 'holdposition',
        10: 'patrol',
        -1: 'garrison',
    }
    weapons = ['weapon_ar2']

class CombineEliteUnlock(AbilityUpgrade):
    name = 'combine_elite_unlock'
    displayname = 'Combine Elite Soldier Unlock'
    description = ''
    image_name = "vgui/combine/abilities/combine_elite_unlock"
    buildtime = 95.0
    costs = [[('requisition', 50)], [('kills', 5)]]

class CombineEliteInfo(CombineSharedInfo):
    name = 'unit_combine_elite'
    displayname = 'Combine Elite Soldier'
    description = ''
    image_name = 'vgui/combine/units/unit_combine_elite'
    portrait = 'resource/portraits/combineAR2.bik'
    costs = [[('requisition', 60), ('power', 40)], [('kills', 4)]]
    buildtime = 36.0
    health = 250
    maxspeed = 208
    sensedistance = 1024.0
    viewdistance = 896
    attributes = ['heavy']
    techrequirements = ['weaponar2_comb_unlock']
    selectionpriority = 4
    sound_select = 'unit_combine_elite_select'
    sound_move = 'unit_combine_elite_move'
    sound_attack = 'unit_combine_elite_attack'
    modelname = 'models/combine_super_soldier.mdl'
    #tier = 3
    abilities = {
        0: 'combineball',
        2: 'weaponswitch_ar2',
        3: 'weaponswitch_shotgun',
        7: 'mountturret',
        8: 'attackmove',
        9: 'holdposition',
        10: 'patrol',
        -1: 'garrison',
    }
    weapons = ['weapon_shotgun', 'weapon_ar2']
    #accuracy = 'medium'
    population = 1

class CombineHeavyInfo(CombineSharedInfo):
    name = 'unit_combine_heavy'
    cls_name = 'unit_combineheavy'
    displayname = 'Combine Wallhammer Soldier'
    description = ''
    image_name = 'vgui/combine/units/unit_combine_heavy'
    costs = [[('requisition', 55), ('power', 30)], [('kills', 4)]]
    buildtime = 32.0
    health = 300
    maxspeed = 224
    sensedistance = 896.0
    viewdistance = 768
    unitenergy = 350
    unitenergy_initial = -1
    attributes = ['heavy']
    techrequirements = ['build_comb_specialops','weaponsg_comb_unlock']
    selectionpriority = 3
    sound_select = 'unit_combine_elite_select'
    sound_move = 'unit_combine_elite_move'
    sound_attack = 'unit_combine_elite_attack'
    modelname = 'models/combine_heavy.mdl'
    coef = 0.25
    energyforarmor = 20 
    regenerationamount = 10
    regenerationtime = 2
    abilities = {
        #7: 'mountturret',
        0: 'stungrenade',
        8: 'attackmove',
        9: 'holdposition',
        10: 'patrol',
        -1: 'garrison',
    }
    weapons = ['weapon_pulse_shotgun']
    #accuracy = 'medium'
    population = 1	


class CombineSniperUnlock(AbilityUpgrade):
    name = 'combine_sniper_unlock'
    displayname = 'Combine Sniper Soldier Unlock'
    description = '#CombSniperUnlock_Description'
    image_name = 'vgui/combine/abilities/combine_sniper_unlock'
    buildtime = 95.0
    costs = [[('requisition', 40)], [('kills', 4)]]

class CombineSniperInfo(CombineSharedInfo):
    name = 'unit_combine_sniper'
    cls_name = 'unit_combinesniper'
    displayname = 'Combine Sniper Soldier'
    description = ''
    image_name = 'vgui/combine/units/unit_combine_sniper'
    portrait = 'resource/portraits/combineSMG.bik'
    costs = [[('requisition', 50), ('power', 20)], [('kills', 4)]]
    buildtime = 28.0
    health = 200
    maxspeed = 168.0
    sensedistance = 1664.0
    viewdistance = 896
    unitenergy = 60
    unitenergy_initial = 30
    #techrequirements = ['combine_sniper_unlock']
    attributes = ['medium']
    sound_select = 'unit_combine_select'
    sound_move = 'unit_combine_move'
    sound_attack = 'unit_combine_attack'
    modelname = 'models/combine_soldier.mdl'
    #accuracy = 0.75
    #tier = 3
    abilities = {
        0: 'marksmanshot',
        1: 'infiltrate_comb_sniper',
        2: 'steadyposition',
        8: 'attackmove',
        9: 'holdposition',
        10: 'patrol',
        -1: 'garrison',
    }
    weapons = ['weapon_sniperrifle']
    #accuracy = 'high'
    population = 1
    cantakecover = True
    sniperenemy = False

# OVERRUN VERSIONS
class OverrunCombineInfo(CombineInfo):
    name = 'overrun_unit_combine'
    hidden = True
    buildtime = 0
    techrequirements = ['or_tier2_research']
    tier = 0
    costs = [('kills', 5)]
    abilities = {
        0: 'overrun_grenade',
        7: 'mountturret',
        8: 'attackmove',
        9: 'holdposition',
        10: 'patrol',
        -1: 'garrison',
    }

class OverrunCombineSGInfo(CombineSGInfo):
    name = 'overrun_unit_combine_sg'
    hidden = True
    buildtime = 0
    techrequirements = ['or_tier2_research']
    tier = 0
    costs = [('kills', 7)]
    abilities = {
        0: 'overrun_grenade',
        7: 'mountturret',
        8: 'attackmove',
        9: 'holdposition',
        10: 'patrol',
        -1: 'garrison',
    }

class OverrunCombineAR2Info(CombineAR2Info):
    name = 'overrun_unit_combine_ar2'
    hidden = True
    buildtime = 0
    techrequirements = ['or_tier2_research']
    tier = 0
    costs = [('kills', 9)]
    abilities = {
        0: 'overrun_grenade',
        7: 'mountturret',
        8: 'attackmove',
        9: 'holdposition',
        10: 'patrol',
        -1: 'garrison',
    }

class OverrunCombineHeavyInfo(CombineHeavyInfo):
    name = 'overrun_unit_combine_heavy'
    costs = [('kills', 12)]
    techrequirements = ['or_tier3_research']
    #population = 1
    abilities = {
        0: 'overrun_stungrenade',
        7: 'mountturret',
        8: 'attackmove',
        9: 'holdposition',
        10: 'patrol',
        -1: 'garrison',
    }
    buildtime = 0
class OverrunCombineEliteInfo(CombineEliteInfo):
    name = 'overrun_unit_combine_elite'
    costs = [('kills', 20)]
    hidden = True
    buildtime = 0
    techrequirements = ['or_tier3_research']
    tier = 0
    abilities = {
        0: 'combineball_overrun',
        2: 'weaponswitch_ar2',
        3: 'weaponswitch_shotgun_overrun',
        7: 'mountturret',
        8: 'attackmove',
        9: 'holdposition',
        10: 'patrol',
        -1: 'garrison',
    }

class OverrunCombineSniperInfo(CombineSniperInfo):
    name = 'overrun_unit_combine_sniper'
    costs = [('kills', 20)]
    hidden = True
    buildtime = 0
    techrequirements = ['or_tier3_research']
    tier = 0
class OverrunEnemyCombineSniperInfo(CombineSniperInfo):
    name = 'enemy_unit_combine_sniper'
    sniperenemy = True
    
# Transform abilities combine soldier
class TransformToCombineSG(AbilityTransformUnit):
    name = 'combine_transform_sg'
    displayname = '#CombTransSG_Name'
    description = '#CombTransSG_Description'
    image_name = 'vgui/combine/abilities/combine_transform_sg'
    transform_type = 'unit_combine_sg'
    transform_time = 5
    replaceweapons = True
    techrequirements = ['weaponsg_comb_unlock']
    #techrequirements = ['build_comb_armory']
    costs = [('power', 5)]
    activatesoundscript = 'ability_combine_shotgun_upgrade'

class TransformToCombineAR2(AbilityTransformUnit):
    name = 'combine_transform_ar2'
    displayname = '#CombTransAR2_Name'
    description = '#CombTransAR2_Description'
    image_name = 'vgui/combine/abilities/combine_transform_ar2'
    transform_type = 'unit_combine_ar2'
    transform_time = 7.0
    replaceweapons = True
    techrequirements = ['weaponar2_comb_unlock']
    #techrequirements = ['build_comb_armory']
    costs = [('power', 10)]
    activatesoundscript = 'ability_combine_ar2_upgrade'

# Mission Versions
class MissionCombineInfo(CombineInfo):
    name = 'mission_unit_combine'
    hidden = True
    health = 75
    scrapdropchance = 0.0
    abilities = {
        0: 'mission_grenade',
        8: 'attackmove',
        9: 'holdposition',
        10: 'patrol',
    }

# =========================================================================================================================================
# ============================================================ Character Units ============================================================
# =========================================================================================================================================

@entity('char_combine_canshootmove', networked=True, )
class CharacterUnitCanShootMove(UnitCombine):
    def OnTakeDamage(self, dmginfo):
        if self.lasttakedamage and self.health > 0 and dmginfo.GetDamage() > 0:
            self.EmitSound("unit_combine_hurt")
        return super().OnTakeDamage(dmginfo)

    # Settings
    canshootmove = True


@entity('character_unit', networked=True, )
class CharacterUnit(UnitCombine):
    def OnTakeDamage(self, dmginfo):
        if self.lasttakedamage and self.health > 0 and dmginfo.GetDamage() > 0:
            self.EmitSound("unit_combine_hurt")
        return super().OnTakeDamage(dmginfo)

    # Settings
    # canshootmove = True

class CharacterCombineSoldier(CombineInfo):
    name = 'char_combine_soldier'
    cls_name = 'char_combine_canshootmove'
    displayname = '#CharCombAssault_Name'
    description = '#CharCombAssault_Description'
    maxspeed = 240
    viewdistance = 800
    health = 1000
    buildtime = 0.01
    scrapdropchance = 1.0
    costs = []
    population = 1
    attributes = ['assault']
    techrequirements = []
    tier = 0
    weapons = ['weapon_shotgun', 'weapon_ar2']
    abilities = {
        0: 'grenade_soldier',
        2: 'weaponswitch_ar2_char',
        3: 'weaponswitch_shotgun_char',
        7: 'mountturret',
        8: 'attackmove',
        9: 'holdposition',
        10: 'patrol',
    }
    recharge_other_abilities = {
        'char_combine_soldier',
        'char_combine_elite',
        'char_metropolice_support',
        'char_metropolice_tank',
        'char_metropolice_scout',
        'char_rebel_scout',
        'char_rebel_flamer',
        'char_rebel_veteran',
        'char_rebel_rpg',
        'char_rebel_engineer',
        'char_rebel_medic',
        'char_rebel_soldier',
    }
    rechargetime = 180.0

class CharacterEliteSoldier(CombineEliteInfo):
    name = 'char_combine_elite'
    displayname = '#CharCombElite_Name'
    description = '#CharCombElite_Description'
    techrequirements = []
    maxspeed = 230
    viewdistance = 800
    health = 800
    buildtime = 0.01
    scrapdropchance = 1.0
    accuracy = 1.5
    costs = []
    population = 1
    tier = 0
    attributes = ['dps']
    weapons = ['weapon_ar2']
    abilities = {
        0: 'combineball_char',
        7: 'mountturret',
        8: 'attackmove',
        9: 'holdposition',
        10: 'patrol',
    }
    recharge_other_abilities = {
        'char_combine_soldier',
        'char_combine_elite',
        'char_metropolice_support',
        'char_metropolice_tank',
        'char_metropolice_scout',
        'char_rebel_scout',
        'char_rebel_flamer',
        'char_rebel_veteran',
        'char_rebel_rpg',
        'char_rebel_engineer',
        'char_rebel_medic',
        'char_rebel_soldier',
    }
    rechargetime = 180.0