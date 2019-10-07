description = "VHF cnc450";
vendor = "Arne Böckmann";
vendorUrl = "github.com/arneboe";
legal = "Do whatever you want license";
certificationLevel = 2;

longDescription = "Use this post to understand which information is available when developing a new post. The post will output the primary information for each entry function being called.";

extension = "cnc";


capabilities = CAPABILITY_MILLING;

allowMachineChangeOnSection = true;
allowHelicalMoves = true;
allowSpiralMoves = true;
// do not allow circular motion. Everything will be linear interpolated
allowedCircularPlanes = 0; 
//since we do not allow circular paths the following settings are ignored
//maximumCircularSweep = toRad(1000000);
//minimumCircularRadius = spatial(0.001, MM);
//maximumCircularRadius = spatial(1000000, MM);

/**Specifies whether the work plane is mapped to the model
 * origin and work plane.
 * When disabled the post is responsible for
 * handlingmappingfrom the model origin to the setup origin.*/
mapToWCS = true;

/** Specifies whether the coordinates are mapped to 
 * the work planeorigin. When disabled the post is responsible 
 * for handling the work plane origin.  */
mapWorkOrigin = true;

/**Specifies whether the program namemust be an integer */
programNameIsInteger = false;

/**Contains the output unitsof the post processor. 
 * Only MM or IN are allowed. However we output hpgl units...
 * Thus this is rather useless :-) */
unit = MM;

// user-defined properties
properties = {
    dummy: true, // show the commonly interesting current state
  };

  // user-defined property definitions
propertyDefinitions = {
    dummy: {title:"dummy bool prop", description:"Lorem bla bla", type:"boolean"},
  };


//format definitions
//TODO maybe?!
var linFormat = createFormat({decimals:0});


function dump(name, _arguments) {

    writeln(name);
}

/** Post processor initialization */
function onOpen()
{
    //do init
     //TODO no idea!
    writeln("^s0;")

    //maybe setting the maximum line length to 5mm?! FIXME
    writeln("AP5000,5000,5000;")

    //set the table dimensions in um
    writeln("CO790000,1024000,160000;")

    //TODO no idea FIXME
    writeln("VB200,200,200;")

    //TODO no idea
    writeln("RV2500,300;")

    //TODO no idea. Doc says "adjustment drive" but dont know what that means
    //might be moving to each endanschlag...
    writeln("RF;")

    //set ports one and two to zero.
    //those ports contain the bits for spindel speed and the custom output pins.
    writeln("SO1,0;")
    writeln("SO2,0;")
}

/** Each parameter setting */
function onParameter(string, value)
{

}

/**Start of an operation */
function onSection()
{

}

/**End of an operat */
function onSectionEnd()
{

}

/**Start of a special cycle operation (Stock Transfer) */
function onSectionSpecialCycle()
{
    //TODO no idea what this is
}

/**End of a special cycle operation */
function onSectionEndSpecialCycle()
{
    //TODO no idea if needed
}

/** Start of a cycle*/
function onCycle() 
{

}

/** Each cycle point */
function onCyclePoint(x, y, z)
{

}

/** End of a cycle */
function onCycleEnd()
{

}

/** spindle speed changes */
function onSpindleSpeed(value)
{

}

/** Converts mm to cnc450 units */
function convertMM(value)
{
    //TODO no idea what this is.
    //For now just assume um
    return value * 1000
}

/** Convert speed from mm/s to steps */
function convertSpeed(speed)
{
    //FIXME make sure that input speed is in mm?!
    //80 steps = 1mm
    return speed * 80;
}


var lastFeed = -1;
var lastX = -1;
var lastY = -1;
var lastZ = -1;

/**3-axis cutting move */
function onLinear(x, y, z, feed)
{
    /** (1) check if feed has changed from last time. Update if yes
     *  (2) convert mm to hpgl units
     *  (2) output x/y
     *  (3) output z
     */

    if(lastFeed != feed)
    {
        lastFeed = feed;
        feed_conv = linFormat.format(convertSpeed(feed));
        writeln("EU" + feed_conv + ";");
    }

    if(lastX != x || lastY != y)
    {
        lastX = x;
        lastY = y;
        x_conv = linFormat.format(convertMM(x));
        y_conv = linFormat.format(convertMM(y));
        writeln("PA" + x_conv + "," + y_conv + ";");
    }

    if(lastZ != z)
    {
        lastZ = z;
        z_conv = linFormat.format(convertMM(z));
        writeln("ZA" + z_conv + ";");
    }
}

/**3-axis rapid move */
function onRapid(x, y, z)
{
    //there is no special rapid mode. Just use linear.
    onLinear(x, y, z, 2000)
}

/** Circular move */
function onCircular(clockwise, cx, cy, cz, x, y, z, feed)
{

}

/** Dwell Manual NC command */
function onDwell(value)
{

}


/** End of post processing */
function onClose()
{

}

/**Post processing has completed, output files are closed */
function onTerminate()
{

}

/**Movement type changes */
function onMovement(value)
{

}

/**Machine configuration changes */
function onMachine()
{

}

/**Manual NC command not handled in its own function */
function onCommand(value)
{

}

/**Comment Manual NC command */
function onComment(string)
{

}

/** 5-d linear move */
function onLinear5D(x, y, z, a, b, c, feed)
{
    //TODO throw not supported!
}

/**Spindle orientation is requested */
function onOrientateSpindle(value)
{

}

/**Pass through Manual NC command */
function onPassThrough(string)
{

}

/** Power mode for water/plasma/laser changes */
function onPower(boolean)
{
    //TODO throw not supported
}

/**Radius compensation mode changes */
function onRadiusCompensation()
{
    //TODO probly need to do something here
}

/**Rotary axes limits are exceeded */
function onRewindMachine(a, b, c)
{
    //TODO throw not supported
}

/** Tool compensation mode changes */
function onToolCompensation(value)
{
    //TODO no idea if needed
}