/** @odoo-module **/

// ensure components are registered beforehand.
// import SignerMenuView from "./signer_menu_view.esm";
import {getMessagingComponent} from "@mail/utils/messaging_component";

const {Component} = owl;

export class SignerMenuContainer extends Component {
    /**
     * @override
     */
    setup() {
        super.setup();
        this.env.services.messaging.modelManager.messagingCreatedPromise.then(() => {
            this.signerMenuView =
                this.env.services.messaging.modelManager.messaging.models.SignerMenuView.insert();
            this.render();
        });
    }
}

Object.assign(SignerMenuContainer, {
    components: {SignerMenuView: getMessagingComponent("SignerMenuView")},
    template: "sign_oca.SignerMenuContainer",
});
