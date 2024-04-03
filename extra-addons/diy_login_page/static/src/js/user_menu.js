/** @odoo-module **/

import { registry } from "@web/core/registry";
import { WebClient } from "@web/webclient/webclient";
import { patch } from 'web.utils';

// 必须引用，否则加载不出菜单，导致移除失败
import { preferencesItem } from "@web/webclient/user_menu/user_menu_items";

registry.category("user_menuitems").remove('documentation');
registry.category("user_menuitems").remove('support');
registry.category("user_menuitems").remove('shortcuts');
registry.category("user_menuitems").remove('separator');
registry.category("user_menuitems").remove('profile');
registry.category("user_menuitems").remove('odoo_account');


registry.category("systray").remove('SwitchCompanyMenu');
registry.category("systray").remove('mail.ActivityMenu');
registry.category("systray").remove('mail.MessagingMenuContainer');
registry.category("systray").remove('mail.CallSystrayMenuContainer');
// registry.category("systray").remove('burger_menu');


// patch(WebClient.prototype, "sd_theme.WebParts", {
//     setup(){
//         this._super()
//         this.title.setParts({ zopenerp: "KAMAX EHS问题处理系统" });
//     }
// })


// const title_service = registry.category('services').get("title");
// console.log(title_service);
// title_service.setParts({ zopenerp: "WXSUDO" });

// TODO 自定义自己的用户修改页面, 替换原有的profile

// export function hrPreferencesItem(env)  {
//     return Object.assign(
//         {},
//         preferencesItem(env),
//         {
//             description: env._t('My Profile'),
//         }
//     );
// }

//registry.category("user_menuitems").add('profile2', hrPreferencesItem, { force: true })