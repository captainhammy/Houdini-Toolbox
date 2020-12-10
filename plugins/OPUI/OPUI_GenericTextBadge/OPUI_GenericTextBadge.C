
#include <HOM/HOM_Module.h>

#include <OP/OP_Node.h>

#include <OPUI/OPUI_GraphBadge.h>
#include <OPUI/OPUI_GraphDisplayOptions.h>
#include <OPUI/OPUI_GraphProxyDescriptor.h>
#include <OPUI/OPUI_GraphTextBadge.h>

#include "OPUI_GenericTextBadge.h"


bool
opuiGenericTextBadgeTest(const OPUI_GraphProxyDescriptor &desc,
	OP_Context &context,
	UT_StringHolder &text,
	UT_Color &clr)
{
    OP_Node	*node = static_cast<OP_Node *>(desc.myItem);

    UT_StringHolder generic_text, generic_text_color;
    UT_Color color;

    if (node && node->hasUserData(TEXT_BADGE_DATA_NAME))
    {
        node->getUserData(TEXT_BADGE_DATA_NAME, generic_text);

        if (generic_text.length() > 0)
        {
            text = generic_text;

            if (node->hasUserData(TEXT_BADGE_COLOR_DATA_NAME))
            {
                node->getUserData(TEXT_BADGE_COLOR_DATA_NAME, generic_text_color);
                color.setColorByName(generic_text_color);
            }

            else
            {
                color = UT_WHITE;
            }

            clr = color;

            return true;
        }
    }

    return false;
}

void
OPUIaddTextBadges(OPUI_GraphTextBadgeArray *add_textbadges)
{
    add_textbadges->append(
        OPUI_GraphTextBadge(
            "generictextbadge", OPUI_GraphTextBadge::theMainTextBadgeCategory,
            "HT Generic Text Badge", TEXT_BADGE_ICON_NAME, 0.0,
            TEXTBADGEVIS_TRUNCATED,
            opuiGenericTextBadgeTest,
            TEXTBADGE_MULTI_THREADED
        )
    );
}
// Dummy to avoid missing symbol errors on load.
void
OPUIaddBadges(OPUI_GraphBadgeArray *add_badges)
{}

