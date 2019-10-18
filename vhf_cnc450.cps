description = "VHF cnc450";
vendor = "Arne Böckmann";
vendorUrl = "github.com/arneboe";
legal = "Do whatever you want license";
certificationLevel = 2;

longDescription = "Use this post to understand which information is available when developing a new post. The post will output the primary information for each entry function being called.";

extension = "cnc";


capabilities = CAPABILITY_MILLING;
tolerance = spatial(0.002, MM);
minimumChordLength = spatial(0.01, MM);
minimumCircularRadius = spatial(0.01, MM);
maximumCircularRadius = spatial(1000, MM);
minimumCircularSweep = toRad(0.01);
maximumCircularSweep = toRad(360);
allowHelicalMoves = false;
allowSpiralMoves = false;
allowedCircularPlanes =  (1 << PLANE_XY); // allow any circular motion

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

/**The output unitsof the post processor.  */
unit = MM;

// user-defined properties
properties = {
    x_offset: 0.0,
    y_offset: 0.0,
    z_offset: 0.0
  };

  // user-defined property definitions
propertyDefinitions = {
    x_offset: {title:"x offset", description:"x offset", type:"float"},
    y_offset: {title:"y offset", description:"y offset", type:"float"},
    z_offset: {title:"z offset", description:"z offset", type:"float"},
  
  };


//format definitions
var xyzFormat = createFormat({decimals:(unit == MM ? 4 : 6)});
var angleFormat = createFormat({decimals:3, scale:DEG});


/** Post processor initialization */
function onOpen()
{
    writeln("THIS_IS_VHF330_G_CODE_DIALECT")
}

/** Each parameter setting */
function onParameter(string, value)
{

}

/**Start of an operation */
function onSection()
{
    writeln("BEGIN_SECTION")
}

/**End of an operat */
function onSectionEnd()
{
    writeln("END_SECTION")
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

function transform_x(x)
{
    return x + properties.x_offset;
}

function transform_y(y)
{
    return y + properties.y_offset;
}

function transform_z(z)
{
    z = z * -1.0;
    return z + properties.z_offset;
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

    x_tf = transform_x(x)
    y_tf = transform_y(y)
    z_tf = transform_z(z)
    x_conv = xyzFormat.format(x_tf)
    y_conv = xyzFormat.format(y_tf)
    z_conv = xyzFormat.format(z_tf)
    f_conv = xyzFormat.format(feed)
    writeln("G1 X" + x_conv +" Y" + y_conv +" Z" + z_conv + " F" + f_conv)
}

/**3-axis rapid move */
function onRapid(x, y, z)
{
    x_tf = transform_x(x)
    y_tf = transform_y(y)
    z_tf = transform_z(z)
    x_conv = xyzFormat.format(x_tf)
    y_conv = xyzFormat.format(y_tf)
    z_conv = xyzFormat.format(z_tf)
    writeln("G0 X" + x_conv +" Y" + y_conv +" Z" + z_conv)
}

/** Circular move */
function onCircular(clockwise, cx, cy, cz, x, y, z, feed) {
    if (isHelical() || (getCircularPlane() != PLANE_XY)) {
      linearize(tolerance);
      return;
    }

    //hack to linearize if arc doesnt fit 
    cx_tf = transform_x(cx)
    cy_tf = transform_y(cy)

    //FIXME should be properties
    if(cx_tf <= 0.1 || cx_tf >= 790.0)
    {
        linearize(tolerance);
        return;
    }
    if(cy_tf <= 0.1 || cy_tf >= 1000.0)
    {
        linearize(tolerance);
        return;
    }

    cx_conv = xyzFormat.format(cx_tf)
    cy_conv = xyzFormat.format(cy_tf)
    angle = angleFormat.format((clockwise ? -1 : 1) * getCircularSweep())
    f_conv = xyzFormat.format(feed)

    writeln("GAA cX" + cx_conv + " cY" + cy_conv + " A" + angle + " F" + f_conv)
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