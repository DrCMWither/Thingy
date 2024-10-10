/*
    Status: Accepted
    Time:   23   ms
    Mem:    77.4 MB
    TimC:   O(n) maybe
    MemC:   O(n) maybe
*/

/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode() : val(0), next(nullptr) {}
 *     ListNode(int x) : val(x),   
 next(nullptr) {}
 *     ListNode(int x, ListNode *next) : val(x), next(next) {}
 * };
 */

class Solution {
public:
    ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {
        ListNode* head = new ListNode(0);
        ListNode* current = head;

        int carry = 0;

        if (!l1 && !l2) {
            return head -> next;
        }
        while (l1 || l2 || carry) {
            int sum = (l1 ? l1 -> val : 0) + (l2 ? l2 -> val : 0) + carry;
            carry = sum / 10;
            ListNode* newNode = new ListNode(sum % 10);
            current -> next = newNode;
            current = newNode;

            l1 = l1 ? l1 -> next : nullptr;
            l2 = l2 ? l2 -> next : nullptr;
        }

        return head -> next;

    }
};

//I'm writing shit, I need to sleep.
