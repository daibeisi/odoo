# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from datetime import date

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.mail.tests.common import MailCommon
from odoo.tests.common import Form, users, warmup
from odoo.tests import tagged
from odoo.tools import formataddr, mute_logger


@tagged('mail_performance', 'account_performance', 'post_install_l10n', 'post_install', '-at_install')
class BaseMailAccountPerformance(AccountTestInvoicingCommon, MailCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # ensure print params
        cls.user_accountman = cls.env.user  # main account setup shadows users, better save it
        cls.company_main = cls.company_data['company']
        cls.company_main.invoice_is_email = True
        cls.company_main.invoice_is_print = False
        cls.move_template = cls.env['mail.template'].create({
            'auto_delete': True,
            'body_html': '<p>TemplateBody for <t t-out="object.name"></t><t t-out="object.invoice_user_id.signature or \'\'"></t></p>',
            'description': 'Sent to customers with their invoices in attachment',
            'email_from': "{{ (object.invoice_user_id.email_formatted or user.email_formatted) }}",
            'mail_server_id': cls.mail_server_global.id,
            'model_id': cls.env['ir.model']._get_id('account.move'),
            'name': "Invoice: Test Sending",
            'partner_to': "{{ object.partner_id.id }}",
            'subject': "{{ object.company_id.name }} Invoice (Ref {{ object.name or 'n/a' }})",
            'report_template_ids': [(4, cls.env.ref('account.account_invoices').id)],
            'lang': "{{ object.partner_id.lang }}",
        })
        cls.attachments = cls.env['ir.attachment'].create(
            cls._generate_attachments_data(
                2, cls.move_template._name, cls.move_template.id
            )
        )
        cls.move_template.write({
            'attachment_ids': [(6, 0, cls.attachments.ids)]
        })

        # test users + fetch admin user for testing (recipient, ...)
        cls.user_account = cls.env['res.users'].with_context(cls._test_context).create({
            'company_id': cls.company_main.id,
            'company_ids': [
                (6, 0, (cls.company_data['company'] + cls.company_data_2['company']).ids)
            ],
            'country_id': cls.env.ref('base.be').id,
            'email': 'e.e@example.com',
            'groups_id': [
                (6, 0, [cls.env.ref('base.group_user').id,
                        cls.env.ref('account.group_account_invoice').id,
                        cls.env.ref('base.group_partner_manager').id
                       ])
            ],
            'login': 'user_account',
            'name': 'Ernest Employee',
            'notification_type': 'inbox',
            'signature': '--\nErnest',
        })
        cls.user_account_other = cls.env['res.users'].with_context(cls._test_context).create({
            'company_id': cls.company_admin.id,
            'company_ids': [(4, cls.company_admin.id)],
            'country_id': cls.env.ref('base.be').id,
            'email': 'e.e.other@example.com',
            'groups_id': [
                (6, 0, [cls.env.ref('base.group_user').id,
                        cls.env.ref('account.group_account_invoice').id,
                        cls.env.ref('base.group_partner_manager').id
                       ])
            ],
            'login': 'user_account_other',
            'name': 'Eglantine Employee',
            'notification_type': 'inbox',
            'signature': '--\nEglantine',
        })

        # mass mode: 10 invoices with their customer
        country_id = cls.env.ref('base.be').id
        langs = ['en_US', 'es_ES']
        cls.env['res.lang']._activate_lang('es_ES')
        cls.test_customers = cls.env['res.partner'].create([
            {'country_id': country_id,
             'email': f'test_partner_{idx}@test.example.com',
             'mobile': f'047500{idx:2d}{idx:2d}',
             'lang': langs[idx % len(langs)],
             'name': f'Partner_{idx}',
            } for idx in range(0, 10)
        ])
        cls.test_account_moves = cls.env['account.move'].create([{
            'invoice_date': date(2022, 3, 2),
            'invoice_date_due': date(2022, 3, 10),
            'invoice_line_ids': [
                (0, 0, {'name': 'Line1',
                        'price_unit': 100.0
                       }
                ),
                (0, 0, {'name': 'Line2',
                        'price_unit': 200.0
                       }
                ),
            ],
            'invoice_user_id': cls.user_account_other.id,
            'move_type': 'out_invoice',
            'name': f'INVOICE_{idx:02d}',
            'partner_id': cls.test_customers[idx].id,
        } for idx in range(0, 10)])

        # test impact of multi language support
        cls._activate_multi_lang(
            test_record=cls.test_account_moves,
            test_template=cls.move_template,
        )

    def setUp(self):
        super().setUp()

        # setup mail gateway to simulate complete reply-to computation
        self._init_mail_gateway()

        # patch registry to simulate a ready environment
        self.patch(self.env.registry, 'ready', True)
        self.flush_tracking()


@tagged('mail_performance', 'account_performance', 'post_install_l10n', 'post_install', '-at_install')
class TestAccountComposerPerformance(BaseMailAccountPerformance):
    """ Test performance of custom composer for moves. """

    @users('user_account')
    @warmup
    @mute_logger('odoo.addons.mail.models.mail_mail', 'odoo.models.unlink')
    def test_move_composer_multi(self):
        """ Test with mailing mode """
        test_moves = self.test_account_moves.with_env(self.env)
        test_customers = self.test_customers.with_env(self.env)
        move_template = self.move_template.with_env(self.env)

        for test_move in test_moves:
            self.assertFalse(test_move.is_move_sent)

        # QueryCount: 22
        default_ctx = test_moves.action_send_and_print()['context']
        default_ctx['default_template_id'] = move_template.id
        composer_form = Form(
            self.env['account.invoice.send'].with_context(default_ctx)
        )
        composer = composer_form.save()

        # QueryCount: 356 on l10n staging (l10n_generic_coa: 252 / com 288 / ent 290)
        with self.mock_mail_gateway(mail_unlink_sent=False):
            composer.send_and_print_action()

        # check results: emails (mailing mode when being in multi)
        self.assertEqual(len(self._mails), 10, 'Should send an email to each invoice')
        for move, customer in zip(test_moves, test_customers):
            with self.subTest(move=move, customer=customer):
                if move.partner_id.lang == 'es_ES':
                    _exp_body_tip = f'SpanishBody for {move.name}'
                    _exp_move_name = f'Factura borrador {move.name}'
                    _exp_report_name = f'Factura borrador {move.name}.html'
                    _exp_subject = f'SpanishSubject for {move.name}'
                else:
                    _exp_body_tip = f'TemplateBody for {move.name}'
                    _exp_move_name = move.display_name
                    _exp_report_name = f'Draft Invoice {move.name}.html'
                    _exp_subject = f'{self.env.user.company_id.name} Invoice (Ref {move.name})'

                self.assertEqual(move.partner_id, customer)
                self.assertMailMail(
                    customer,
                    'sent',
                    author=self.user_account.partner_id,  # author: current user, not synchronized with email_from of template
                    content=_exp_body_tip,
                    email_values={
                        'attachments_info': [
                            {'name': 'AttFileName_00.txt', 'raw': b'AttContent_00', 'type': 'text/plain'},
                            {'name': 'AttFileName_01.txt', 'raw': b'AttContent_01', 'type': 'text/plain'},
                            {'name': _exp_report_name, 'type': 'text/plain'},
                        ],
                        'body_content': _exp_body_tip,
                        'email_from': self.user_account_other.email_formatted,
                        'subject': _exp_subject,
                        'reply_to': formataddr((
                            f'{move.company_id.name} {_exp_move_name}',
                            f'{self.alias_catchall}@{self.alias_domain}'
                        )),
                    },
                    fields_values={
                        'auto_delete': True,
                        'email_from': self.user_account_other.email_formatted,
                        'is_notification': True,  # should keep logs by default
                        'mail_server_id': self.mail_server_global,
                        'subject': _exp_subject,
                        'reply_to': formataddr((
                            f'{move.company_id.name} {_exp_move_name}',
                            f'{self.alias_catchall}@{self.alias_domain}'
                        )),
                    },
                )

        # composer configuration
        self.assertEqual(composer.attachment_ids, self.attachments)
        # self.assertEqual(composer.body, move_template.body_html)
        self.assertEqual(composer.body, '<p>SpanishBody for <t t-out="object.name" /></p>',
                         'TODO: currently composer content is forced with template content using last browsed lang')
        self.assertEqual(composer.composition_mode, 'mass_mail')
        self.assertEqual(composer.invoice_ids, test_moves)
        self.assertTrue(composer.is_email)
        self.assertFalse(composer.is_print)
        self.assertEqual(composer.mail_server_id, self.mail_server_global)
        self.assertEqual(composer.model, test_moves._name)
        self.assertEqual(
            sorted(literal_eval(composer.res_ids)),
            test_moves.ids
        )
        # self.assertEqual(composer.subject, move_template.subject)
        self.assertEqual(composer.subject, 'SpanishSubject for {{ object.name }}',
                         'TODO: currently composer content is forced with template content using last browsed lang')
        self.assertEqual(composer.template_id, move_template)
        # invoice update
        for test_move in test_moves:
            self.assertTrue(test_move.is_move_sent)

    @users('user_account')
    @warmup
    @mute_logger('odoo.addons.mail.models.mail_mail', 'odoo.models.unlink')
    def test_move_composer_single(self):
        """ Test comment mode """
        test_move = self.test_account_moves[0].with_env(self.env)
        test_customer = self.test_customers[0].with_env(self.env)
        move_template = self.move_template.with_env(self.env)

        # QueryCount: 70 on l10n staging (l10n_generic_coa: 53 / com 55)
        default_ctx = test_move.action_send_and_print()['context']
        default_ctx['default_template_id'] = move_template.id
        composer_form = Form(
            self.env['account.invoice.send'].with_context(default_ctx)
        )
        composer = composer_form.save()

        # QueryCount: 100 on l10n staging (l10n_generic_coa: 92 / com 103)
        with self.mock_mail_gateway(mail_unlink_sent=False), \
             self.mock_mail_app():
            composer = composer_form.save()
            composer.send_and_print_action()
            self.env.cr.flush()  # force tracking message

        # check results: comment (post when being in single mode)
        self.assertEqual(len(self._new_msgs), 2, 'Should produce 2 messages: one for posting template, one for tracking')
        print_msg, track_msg = self._new_msgs[0], self._new_msgs[1]
        self.assertNotified(
            print_msg,
            [{
                'is_read': True,
                'partner': test_customer,
                'type': 'email',
            }],
        )

        # print: template-based message
        self.assertEqual(len(print_msg.attachment_ids), 3)
        self.assertNotIn(self.attachments, print_msg.attachment_ids,
                         'Attachments should be duplicated, not just linked')
        self.assertEqual(print_msg.author_id, self.env.user.partner_id,
                         'TODO: not synchronized with email_from choice')
        # self.assertEqual(print_msg.author_id, self.user_account_other.partner_id,
        #                  'Should take invoice_user_id partner')
        self.assertEqual(print_msg.email_from, self.user_account_other.email_formatted,
                         'Should take invoice_user_id email')
        self.assertEqual(print_msg.notified_partner_ids, test_customer + self.user_accountman.partner_id)
        self.assertEqual(print_msg.subject, f'{self.env.user.company_id.name} Invoice (Ref {test_move.name})')
        # tracking: is_move_sent
        self.assertEqual(track_msg.author_id, self.env.user.partner_id)
        self.assertEqual(track_msg.email_from, self.env.user.email_formatted)
        self.assertEqual(track_msg.tracking_value_ids.field.name, 'is_move_sent')
        # sent email
        self.assertMailMail(
            test_customer,
            'sent',
            author=self.user_account.partner_id,  # author: current user, not synchronized with email_from of template
            content=f'TemplateBody for {test_move.name}',
            email_values={
                'attachments_info': [
                    {'name': 'AttFileName_00.txt', 'raw': b'AttContent_00', 'type': 'text/plain'},
                    {'name': 'AttFileName_01.txt', 'raw': b'AttContent_01', 'type': 'text/plain'},
                    {'name': f'Draft Invoice {test_move.name}.html', 'type': 'text/plain'},
                ],
                'body_content': f'TemplateBody for {test_move.name}',
                'email_from': self.user_account_other.email_formatted,
                'subject': f'{self.env.user.company_id.name} Invoice (Ref {test_move.name})',
                'reply_to': formataddr((
                    f'{test_move.company_id.name} {test_move.display_name}',
                    f'{self.alias_catchall}@{self.alias_domain}'
                )),
            },
            fields_values={
                'auto_delete': False,
                'email_from': self.user_account_other.email_formatted,
                'is_notification': True,  # should keep logs by default
                'mail_server_id': self.mail_server_global,
                'subject': f'{self.env.user.company_id.name} Invoice (Ref {test_move.name})',
                'reply_to': formataddr((
                    f'{test_move.company_id.name} {test_move.display_name}',
                    f'{self.alias_catchall}@{self.alias_domain}'
                )),
            },
        )

        # composer configuration
        self.assertEqual(len(composer.attachment_ids), 3)
        self.assertNotIn(self.attachments, composer.attachment_ids,
                         'Attachments should be duplicated, not just linked')
        self.assertIn(f'TemplateBody for {test_move.name}', composer.body)
        self.assertEqual(composer.composition_mode, 'comment')
        self.assertEqual(composer.invoice_ids, test_move)
        self.assertTrue(composer.is_email)
        self.assertFalse(composer.is_print)
        self.assertEqual(composer.model, test_move._name)
        self.assertEqual(
            sorted(literal_eval(composer.res_ids)),
            test_move.ids
        )
        self.assertEqual(composer.subject, f'{self.env.user.company_id.name} Invoice (Ref {test_move.name})')
        self.assertEqual(composer.template_id, move_template)
        # invoice update
        self.assertTrue(test_move.is_move_sent)

    @users('user_account')
    @warmup
    @mute_logger('odoo.addons.mail.models.mail_mail', 'odoo.models.unlink')
    def test_move_composer_single_lang(self):
        """ Test with another language """
        test_move = self.test_account_moves[1].with_env(self.env)
        test_customer = self.test_customers[1].with_env(self.env)
        move_template = self.move_template.with_env(self.env)

        # QueryCount: 71 on l10n staging (l10n_generic_coa: 54 / com 56)
        default_ctx = test_move.action_send_and_print()['context']
        default_ctx['default_template_id'] = move_template.id
        composer_form = Form(
            self.env['account.invoice.send'].with_context(default_ctx)
        )
        composer = composer_form.save()

        # QueryCount: 101 on l10n staging (l10n_generic_coa: 92 / com 103)
        with self.mock_mail_gateway(mail_unlink_sent=False), \
             self.mock_mail_app():
            composer = composer_form.save()
            composer.send_and_print_action()
            self.env.cr.flush()  # force tracking message

        # check results: comment (post when being in single mode)
        self.assertEqual(len(self._new_msgs), 2, 'Should produce 2 messages: one for posting template, one for tracking')
        print_msg, track_msg = self._new_msgs[0], self._new_msgs[1]
        self.assertNotified(
            print_msg,
            [{
                'is_read': True,
                'partner': test_customer,
                'type': 'email',
            }],
        )

        # print: template-based message
        self.assertEqual(len(print_msg.attachment_ids), 3)
        self.assertNotIn(self.attachments, print_msg.attachment_ids,
                         'Attachments should be duplicated, not just linked')
        self.assertEqual(print_msg.author_id, self.env.user.partner_id,
                         'TODO: not synchronized with email_from choice')
        # self.assertEqual(print_msg.author_id, self.user_account_other.partner_id,
        #                  'Should take invoice_user_id partner')
        self.assertEqual(print_msg.email_from, self.user_account_other.email_formatted,
                         'Should take invoice_user_id email')
        self.assertEqual(print_msg.notified_partner_ids, test_customer + self.user_accountman.partner_id)
        self.assertEqual(print_msg.subject, f'SpanishSubject for {test_move.name}')
        # tracking: is_move_sent
        self.assertEqual(track_msg.author_id, self.env.user.partner_id)
        self.assertEqual(track_msg.email_from, self.env.user.email_formatted)
        self.assertEqual(track_msg.tracking_value_ids.field.name, 'is_move_sent')
        # sent email
        self.assertMailMail(
            test_customer,
            'sent',
            author=self.user_account.partner_id,  # author: current user, not synchronized with email_from of template
            content=f'SpanishBody for {test_move.name}',  # translated version
            email_values={
                'attachments_info': [
                    {'name': 'AttFileName_00.txt', 'raw': b'AttContent_00', 'type': 'text/plain'},
                    {'name': 'AttFileName_01.txt', 'raw': b'AttContent_01', 'type': 'text/plain'},
                    {'name': f'Factura borrador {test_move.name}.html', 'type': 'text/plain'},
                ],
                'body_content': f'SpanishBody for {test_move.name}',  # translated version
                'email_from': self.user_account_other.email_formatted,
                'subject': f'SpanishSubject for {test_move.name}',  # translated version
                'reply_to': formataddr((
                    f'{test_move.company_id.name} {test_move.display_name}',
                    f'{self.alias_catchall}@{self.alias_domain}'
                )),
            },
            fields_values={
                'auto_delete': False,
                'email_from': self.user_account_other.email_formatted,
                'is_notification': True,  # should keep logs by default
                'mail_server_id': self.mail_server_global,
                'subject': f'SpanishSubject for {test_move.name}',  # translated version
                'reply_to': formataddr((
                    f'{test_move.company_id.name} {test_move.display_name}',
                    f'{self.alias_catchall}@{self.alias_domain}'
                )),
            },
        )

        # composer configuration
        self.assertEqual(len(composer.attachment_ids), 3)
        self.assertNotIn(self.attachments, composer.attachment_ids,
                         'Attachments should be duplicated, not just linked')
        self.assertIn(f'SpanishBody for {test_move.name}', composer.body,
                      'Should be translated, based on template')
        self.assertEqual(composer.composition_mode, 'comment')
        self.assertEqual(composer.invoice_ids, test_move)
        self.assertTrue(composer.is_email)
        self.assertFalse(composer.is_print)
        self.assertEqual(composer.model, test_move._name)
        self.assertEqual(
            sorted(literal_eval(composer.res_ids)),
            test_move.ids
        )
        self.assertEqual(composer.subject, f'SpanishSubject for {test_move.name}',
                         'Should be translated, based on template')
        self.assertEqual(composer.template_id, move_template)
        # invoice update
        self.assertTrue(test_move.is_move_sent)
