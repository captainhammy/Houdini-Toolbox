
#include <HOM/HOM_Module.h>

#include <OP/OP_Node.h>

#include <OPUI/OPUI_GraphBadge.h>
#include <OPUI/OPUI_GraphDisplayOptions.h>
#include <OPUI/OPUI_GraphProxyDescriptor.h>
#include <OPUI/OPUI_GraphTextBadge.h>

#include <UT/UT_DSOVersion.h>

#include "OPUI_GenericImageBadge.h"

static const UT_StringHolder icon_name("NETVIEW_cop2_info");


bool
opuiGenericImageBadgeTest(const OPUI_GraphProxyDescriptor &desc,
        OPUI_GraphBadgeVisibility visibility,
        OP_Context &context,
        UT_StringHolder &icon,
        UT_Color &clr)
{
    OP_Node *node = static_cast<OP_Node *>(desc.myItem);

    UT_StringHolder image_name;

    if (node && node->hasUserData(GENERIC_IMAGE_BADGE_DATA_NAME))
    {
        node->getUserData(GENERIC_IMAGE_BADGE_DATA_NAME, image_name);

        if (image_name.length() > 0)
        {
            icon = UT_StringHolder(image_name);

	        return true;
        }
    }

    return false;
}

void
OPUIaddBadges(OPUI_GraphBadgeArray *add_badges)
{
    add_badges->append(
	    OPUI_GraphBadge(
            "generic_image_badge",
            OPUI_GraphBadge::theMainBadgeCategory,
            "HT Generic Image Badge",
            icon_name,
            BADGEVIS_NORMAL,
            opuiGenericImageBadgeTest,
            BADGE_MULTI_THREADED
        )
    );
}

// Dummy to avoid missing symbol errors on load.
void
OPUIaddTextBadges(OPUI_GraphTextBadgeArray *add_textbadges)
{}
