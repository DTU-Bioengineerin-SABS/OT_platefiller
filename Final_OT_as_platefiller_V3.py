from opentrons import types

#######################
# the high measuring from the bottom of the agar resoware
hight = 0
target_hight = -9 # target high from the top 
#######################

def get_values(*names):
    import json
    _all_values = json.loads("""{"plate_no":"9"}""")
    return [_all_values[n] for n in names]


metadata = {
    'protocolName': 'Opentrons as plate filler 96W',
    'author': 'Vilhelm Krarup Møller (vikmol@dtu.dk)',
    'apiLevel': '2.5'
}


def run(protocol):
    [plate_no] = get_values('plate_no')

    ## Turn on lights while running run
    protocol.set_rail_lights(True)


    p300tips = [protocol.load_labware('opentrons_96_tiprack_300ul', 11)]
    p300 = protocol.load_instrument('p300_multi', 'right', tip_racks=p300tips)

    ## temp deck
    tempdeck = protocol.load_module('Temperature Module', 10)
    heated_agar = tempdeck.load_labware('agilent_1_reservoir_290ml')

    mcirolate_type = 'nest_96_wellplate_200ul_flat'



    # Actively heat the agar
    tempdeck.set_temperature(85)

    ## list of all the micro plate positions
    microplates = [protocol.load_labware(
                mcirolate_type, s) for s in ['7', '8', '9', '4', '5', '6', '1', '2', '3']]

    # set flow rate of pipet
    p300.flow_rate.aspirate = 150#100#70
    p300.flow_rate.dispense = 150#100#80

    ## combe movement to agitate the agar and avoid it from solidifying:
    # Get the center of well A1.
    center_location = heated_agar['A1'].bottom()
    combe_move_right = center_location.move(types.Point(x=50, y=0, z=hight))
    combe_move_left = center_location.move(types.Point(x=-50, y=0, z=hight))

    ## loop through all the plates placed on the table(given by plate_no value):
    p300.pick_up_tip()
    for plate in microplates[0:int(plate_no)]:    

        
        # move the pipet through the trough in a combing motion to avoid solidification of the agar
        p300.move_to(heated_agar['A1'].bottom(hight))
        protocol.max_speeds['X'] = 35 # limit max speed of x to 35 mm/s
        p300.move_to(combe_move_right) # move to right in trough
        p300.move_to(combe_move_left) # move to left in trough
        protocol.max_speeds['X'] = None # reset to default


        # prewetting the tip and settup for reverse pipetting to avoid bobles in agar
        p300.aspirate(175, heated_agar['A1'].bottom(hight))
        p300.dispense(175, heated_agar['A1'].bottom(hight))
        p300.aspirate(140, heated_agar['A1'].bottom(hight))
        p300.dispense(100, heated_agar['A1'].bottom(hight))
        # Will dispense agar in each well in the plate
        """Start poring the agar"""
        for dispense_pos in plate.rows()[0]:
            p300.aspirate(150, heated_agar['A1'].bottom(hight))
            p300.dispense(150, dispense_pos.top(target_hight))
        p300.dispense(35, heated_agar['A1'].bottom(hight))
    
    p300.drop_tip()
        

    ## Turn off lights when run is finished
    protocol.set_rail_lights(False)


    