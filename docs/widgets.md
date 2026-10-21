# Widgets and quick controls (S0.8.4)

| Surface | Platform | Content |
|---|---|---|
| Home screen, small | iOS, Android | One scene button (Good night, Leaving) |
| Home screen, medium | iOS, Android | 4 key lights + thermostat setpoint |
| Lock screen | iOS | Thermostat temperature; next alarm |
| Control Center | iOS 18+ | Scenes, key lights, "talk to the assistant" |
| Action button / Siri Shortcut | iOS | Push-to-talk to the assistant |
| Quick Settings tiles | Android | Scenes, key lights, assistant |
| Actionable notifications | iOS, Android | Doorbell, laundry done, reminder (done / snooze 10 min), door left open |
| Watch complication (optional) | watchOS | Scenes |

Entity ids come from `home-assistant-config/docs/entities.md`; widgets call HA scripts (`script.good_night`, `script.scene_leaving`), never raw device services, so the house logic stays in one place.
