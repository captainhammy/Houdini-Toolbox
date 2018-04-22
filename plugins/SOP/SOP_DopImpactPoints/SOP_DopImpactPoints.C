/*
 * Produced by:
 *      Graham Thompson
 *      captainhammy@gmail.com
 *      www.captainhammy.com
 *
 * Description:
 *      Generate points based on DOP obects Impact record data.
 *
 * Name: SOP_DopImpactPoints.C
 *
*/

#include "SOP_DopImpactPoints.h"

#include <CH/CH_Manager.h>
#include <DOP/DOP_Parent.h>
#include <OP/OP_Operator.h>
#include <OP/OP_OperatorTable.h>
#include <PRM/PRM_Include.h>
#include <PRM/PRM_SpareData.h>
#include <SIM/SIM_Data.h>
#include <SIM/SIM_Object.h>
#include <SIM/SIM_ObjectArray.h>
#include <SIM/SIM_Query.h>
#include <UT/UT_DSOVersion.h>
#include <UT/UT_Options.h>

void newSopOperator(OP_OperatorTable *table)
{
    OP_Operator                 *new_op;

    // Create the new operator.
    new_op = new OP_Operator(
        "dopimpactpoints",
        "Dop Impact Points",
        SOP_DopImpactPoints::myConstructor,
        SOP_DopImpactPoints::myTemplateList,
        0,
        0,
        0,
        0,
        1,
        0
    );

    // Set a different icon name.
    new_op->setIconName("POP_hitinfo");

    // Add it to the table.
    table->addOperator(new_op);
}

OP_Node *
SOP_DopImpactPoints::myConstructor(OP_Network *net,
                                   const char *name,
                                   OP_Operator *op)
{
    return new SOP_DopImpactPoints(net, name, op);
}

SOP_DopImpactPoints::SOP_DopImpactPoints(OP_Network *net,
                                         const char *name,
                                         OP_Operator *op):
    SOP_Node(net, name, op) {}

static PRM_Name names[] =
{
    PRM_Name("doppath", "DOP Network"),
    PRM_Name("normal", "Normal"),
    PRM_Name("impulse", "Impulse"),
    PRM_Name("sourceid", "Source ID"),
    PRM_Name("otherobjid", "Other Object ID"),
    PRM_Name("num_configs", "Number of Configurations")
};

static PRM_Default defaults[] =
{
    PRM_Default(0, ""),
    PRM_Default(1),
    PRM_Default(1),
    PRM_Default(0),
    PRM_Default(0),
    PRM_Default(0)
};

static PRM_Name configNames[] =
{
    PRM_Name("enable#", "Enable"),
    PRM_Name("objpattern#", "Object Mask"),
    PRM_Name("impactpattern#", "Impact Mask"),
    PRM_Name("threshold#", "Impulse Threshold")
};

static PRM_Default configDefaults[] =
{
    PRM_Default(1),
    PRM_Default(0, "*"),
    PRM_Default(0, "*"),
    PRM_Default(0)
};

static PRM_Range configRanges[] =
{
    PRM_Range(PRM_RANGE_RESTRICTED, 0, PRM_RANGE_UI, 1000)
};

static PRM_Template theConfigTemplates[] =
{
    PRM_Template(PRM_TOGGLE, 1, &configNames[0], &configDefaults[0]),
    PRM_Template(PRM_STRING, 1, &configNames[1], &configDefaults[1]),
    PRM_Template(PRM_STRING, 1, &configNames[2], &configDefaults[2]),
    PRM_Template(PRM_FLT_J, 1, &configNames[3], &configDefaults[3], 0, &configRanges[0]),
    PRM_Template()
};

PRM_Template
SOP_DopImpactPoints::myTemplateList[] = {
    PRM_Template(PRM_STRING, PRM_TYPE_DYNAMIC_PATH, 1, &names[0], &defaults[0], 0, 0, 0, &PRM_SpareData::dopPath),
    PRM_Template(PRM_TOGGLE, 1, &names[1], &defaults[1]),
    PRM_Template(PRM_TOGGLE, 1, &names[2], &defaults[2]),
    PRM_Template(PRM_TOGGLE, 1, &names[3], &defaults[3]),
    PRM_Template(PRM_TOGGLE, 1, &names[4], &defaults[4]),
    PRM_Template(PRM_MULTITYPE_LIST, theConfigTemplates, 0, &names[5], &defaults[5], 0, &PRM_SpareData::multiStartOffsetZero),
    PRM_Template()
};

unsigned
SOP_DopImpactPoints::disableParms()
{
    bool                        enabled;
    fpreal                      t = CHgetEvalTime();
    unsigned                    changed, instances;

    changed = 0;
    instances = INSTANCES(t);

    for (int i=0; i<instances; ++i)
    {
        enabled = ENABLED(i, t);
        changed += enableParmInst("objpattern#", &i, enabled);
        changed += enableParmInst("impactpattern#", &i, enabled);
        changed += enableParmInst("threshold#", &i, enabled);
    }

    return changed;
}


OP_ERROR SOP_DopImpactPoints::cookMySop(OP_Context &context)
{
    fpreal                      now, threshold, impulse, otherobjid;
    int                         num_instances, num_objects, objidx;
    unsigned                    records;

    DOP_Parent                  *parent;

    GA_Offset                   pt;
    GA_RWAttributeRef           n_gah, impulse_gah, source_gah, other_gah;
    GA_RWHandleF                impulse_h;
    GA_RWHandleI                source_h, other_h;
    GA_RWHandleV3               n_h;

    OP_Node                     *dopnode;

    SIM_ConstObjectArray        dopobjects, maskobjects;
    const SIM_Object            *dopobject;
    const SIM_Data              *data;
    const SIM_Query             *query;

    UT_String                   doppath, objpattern, objmask;
    UT_OptionEntry              *raw_pos, *raw_n;
    UT_OptionVector3            *pos, *normal;

    now = context.getTime();

    // Clear the detail to remove previous points.
    gdp->clearAndDestroy();

    // Get the path to the DOP Node.
    DOPPATH(doppath, now);

    // Get the number of instances for the multiparm folder.
    num_instances = INSTANCES(now);

    // Get the DOP node from the path.
    dopnode = findNode(doppath);

    // Try to get the DOP parent.
    parent = dopnode ? dopnode->castToDOPParent() : 0;

    // If we got the simulation and have at least one instance.
    if (parent && num_instances > 0)
    {
        // SIM representation of the time.
        SIM_Time sim_time(now);

        // Set the simulation time to now so the simulation cooks properly at
        // the current time.
        parent->setDOPTime(sim_time);

        // Add relationships to the DOP node and simulation.
        addExtraInput(dopnode, OP_INTEREST_DATA);
        addExtraInput(parent->simMicroNode());

        // Add the point Normal attribute.
        if (NORMAL(now))
        {
            // Create the attribute.
            n_gah = gdp->addNormalAttribute(GA_ATTRIB_POINT);

            // Attach a handle.
            n_h.bind(n_gah.getAttribute());
        }

        // Add a point attribute for the impulse values.
        if (IMPULSE(now))
        {
            // Create the attribute.
            impulse_gah = gdp->addFloatTuple(
                GA_ATTRIB_POINT,
                "impulse",
                1,
                GA_Defaults(0.0)
            );

            // Attach a handle.
            impulse_h.bind(impulse_gah.getAttribute());
        }

        // Add a point attribute for the source object id values.
        if (SOURCEID(now))
        {
            // Create the attribute.
            source_gah = gdp->addIntTuple(
                GA_ATTRIB_POINT,
                "sourceid",
                1,
                GA_Defaults(-1)
            );

            // Attach a handle.
            source_h.bind(source_gah.getAttribute());
        }

        // Add a point attribute for the other object id values.
        if (OTHEROBJID(now))
        {
            // Create the attribute.
            other_gah = gdp->addIntTuple(
                GA_ATTRIB_POINT,
                "otherobjid",
                1,
                GA_Defaults(-1)
            );

            // Attach a handle.
            other_h.bind(other_gah.getAttribute());
        }

        // Iterate over each instance in the multiparm block.
        for (int inst=0; inst<num_instances; ++inst)
        {
            // Check to see if this entry is enabled.  If it isn't then we skip
            // this instance.
            if (!ENABLED(inst, now))
            {
                continue;
            }

            // Get the objects to process and mask objects.
            OBJPATTERN(objpattern, inst, now);
            OBJMASK(objmask, inst, now);

            // Get the impulse threshold for the instance.
            threshold = THRESHOLD(inst, now);

            // Get arrays of the DOP objects for the objects to process and
            // mask objects.
            parent->findAllObjectsFromString(objpattern, dopobjects, sim_time);
            parent->findAllObjectsFromString(objmask, maskobjects, sim_time);

            // The number of objects to check for impacts.
            num_objects = dopobjects.entries();

            for (int idx=0; idx<num_objects; ++idx)
            {
                // Get the current object from the list to check.
                dopobject = dopobjects(idx);

                // Search for Impact subdata.
                data = dopobject->getConstNamedSubData("Impacts");

                // If no data was found then we go to the next object.
                if (data == NULL)
                {
                    continue;
                }

                // Get a SIM_Query object so we can get data out of the
                // subdata.
                query = &data->getQueryObject();

                // The number of impact records.
                records = query->getNumRecords("Impacts");

                // For each record.
                for (unsigned rec=0; rec<records; ++rec)
                {
                    // Get the objid of the object the current object is
                    // colliding with.
                    query->getFieldFloat("Impacts", rec, "otherobjid", otherobjid);

                    // Check to see if this objid is in the list of mask
                    // objects.
                    objidx = maskobjects.findPositionById((int)otherobjid);

                    // The object this impact record is for is in the mask list
                    // so now we get the information and create a point at the
                    // location and with the attributes.
                    if (objidx != -1)
                    {
                        // Get the impulse from the collision.
                        query->getFieldFloat("Impacts", rec, "impulse", impulse);

                        // If we have the threshold set higher than 0 and the
                        // impulse is below that threshold then we don't want
                        // to create the point.
                        if (threshold != 0 && threshold > impulse)
                        {
                            continue;
                        }

                        // To get the position and normal vectors we have to
                        // extract the vectors by getting their raw data as
                        // UT_OptionEntry's and then by casting them to a
                        // UT_OptionVector3.  This allows us to get the data
                        // as a UT_Vector3.
                        query->getFieldRaw("Impacts", rec, "position", raw_pos);
                        pos = (UT_OptionVector3 *)raw_pos;

                        // Create a point for this record.
                        pt = gdp->appendPointOffset();

                        // Set the position.
                        gdp->setPos3(pt, pos->getValue());

                        // We need to delete the UT_OptionEntry objects since
                        // they were created by SIM_Query::getFieldRaw.
                        delete raw_pos;

                        // The normal handle will be valid if we said to store
                        // the normal value.
                        if (n_h.isValid())
                        {
                            // Like the position, get the normal information
                            // from the query.
                            query->getFieldRaw("Impacts", rec, "normal", raw_n);
                            normal = (UT_OptionVector3 *)raw_n;

                            // Set the attribute value.
                            n_h.set(pt, normal->getValue());

                            // Delete the entry.
                            delete raw_n;
                        }

                        // Store the impulse value if necessary.
                        if (impulse_h.isValid())
                        {
                            impulse_h.set(pt, impulse);
                        }

                        // Store the objid value if necessary.
                        if (source_h.isValid())
                        {
                            source_h.set(pt, dopobject->getObjectId());
                        }

                        // Store the otherobjid value if necessary.
                        if (other_h.isValid())
                        {
                            other_h.set(pt, (int)otherobjid);
                        }

                    }
                }
            }
        }
    }

    return error();
}

