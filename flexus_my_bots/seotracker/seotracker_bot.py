import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional

from flexus_client_kit import ckit_client
from flexus_client_kit import ckit_cloudtool
from flexus_client_kit import ckit_bot_exec
from flexus_client_kit import ckit_shutdown
from flexus_client_kit import ckit_integrations_db
from flexus_client_kit import ckit_bot_version
from flexus_client_kit.integrations import fi_mongo_store
from flexus_client_kit.integrations import fi_pdoc

logger = logging.getLogger("bot_seotracker")

BOT_NAME = ckit_bot_version.bot_name_from_file(__file__)
SEOTRACKER_ROOTDIR = Path(__file__).parent
SEOTRACKER_SETUP_SCHEMA = json.loads((SEOTRACKER_ROOTDIR / "setup_schema.json").read_text())

SEOTRACKER_INTEGRATIONS: list[ckit_integrations_db.IntegrationRecord] = ckit_integrations_db.static_integrations_load(
    SEOTRACKER_ROOTDIR,
    allowlist=[
        "flexus_policy_document",
        "print_widget",
    ],
    builtin_skills=[],
)

TOOLS = [
    fi_mongo_store.MONGO_STORE_TOOL,
    *[t for rec in SEOTRACKER_INTEGRATIONS for t in rec.integr_tools],
]


async def seotracker_main_loop(fclient: ckit_client.FlexusClient, rcx: ckit_bot_exec.RobotContext) -> None:
    setup = ckit_bot_exec.official_setup_mixing_procedure(SEOTRACKER_SETUP_SCHEMA, rcx.persona.persona_setup)
    integr_objects = await ckit_integrations_db.main_loop_integrations_init(
        SEOTRACKER_INTEGRATIONS, rcx, setup, need_mongo=True
    )

    @rcx.on_tool_call(fi_mongo_store.MONGO_STORE_TOOL.name)
    async def toolcall_mongo_store(toolcall: ckit_cloudtool.FCloudtoolCall, model_produced_args: Dict[str, Any]) -> str:
        return await fi_mongo_store.handle_mongo_store(rcx, toolcall, model_produced_args)

    try:
        while not ckit_shutdown.shutdown_event.is_set():
            await rcx.unpark_collected_events(sleep_if_no_work=10.0)
    finally:
        logger.info("%s exit" % (rcx.persona.persona_id,))


def main():
    from flexus_my_bots.seotracker import seotracker_install
    scenario_fn = ckit_bot_exec.parse_bot_args()
    bot_version = ckit_bot_version.read_version_file(__file__)
    fclient = ckit_client.FlexusClient(ckit_client.bot_service_name(BOT_NAME, bot_version), endpoint="/v1/jailed-bot")

    asyncio.run(ckit_bot_exec.run_bots_in_this_group(
        fclient,
        bot_main_loop=seotracker_main_loop,
        inprocess_tools=TOOLS,
        scenario_fn=scenario_fn,
        install_func=seotracker_install.install,
    ))


if __name__ == "__main__":
    main()
