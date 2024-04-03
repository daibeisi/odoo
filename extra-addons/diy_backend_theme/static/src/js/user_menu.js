/** @odoo-module **/
import { registry } from "@web/core/registry";


registry.category("user_menuitems").remove('documentation');
registry.category("user_menuitems").remove('support');
registry.category("user_menuitems").remove('shortcuts');
registry.category("user_menuitems").remove('separator');
registry.category("user_menuitems").remove('profile');
registry.category("user_menuitems").remove('odoo_account');


registry.category("systray").remove('SwitchCompanyMenu');
registry.category("systray").remove('burger_menu');